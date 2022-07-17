#include <iostream>
#include <vector>
#include <variant>
#include "env.hpp"
#include "drive.hpp"
#include "quote_event.hpp"
#include "timer_event.hpp"
#include "trader_api.hpp"
#include <math.h>

//编写时间:2022.2.14-2.18
//使用StrategySymstem命名空间
namespace SS = StrategySystem;

//创建Drive类模板实例--继承QuoteEvent,TimerEvent,TraderApi类
using drive_t = SS::Drive<SS::QuoteEvent, SS::TimerEvent, SS::TraderApi>;
drive_t *drive;
//套利交易
class PairTrader
{
private:
    // Tick
    sci::RingBufferX *qoute1; //行情地址
    sci::RingBufferX *qoute2;
    int q1AskP[1000], q1BidP[1000], q2AskP[1000], q2BidP[1000]; // tick序列
    int len;
    double tick_size;
    double averSprAsk, averSprBid;
    int OverP1, OverP2;                       //超价
    int TrigOp1, TrigOp2, TrigClo1, TrigClo2; //触发价

    enum class PosStatus
    {
        Empty,
        Long,
        PairTrader,
        Short,
        LongPartialLong,
        LongPartialShort,
        ShortPartialShort,
        ShortPartialLong
    };

    enum class ActionSide
    {
        Long,
        Short,
        Empty
    };

    // Position
    TickerID ticker1, ticker2;
    int32_t LPosTod1, LPosHis1, SPosTod1, SPosHis1, LPosTod2, LPosHis2, SPosTod2, SPosHis2;
    // Order1
    std::vector<int32_t> orderIds1;
    std::vector<int32_t> orderIds2;
    std::vector<int32_t> offsets;
    std::vector<double>closeProfit1;
    std::vector<double>closeProfit2;
    double bPrice1, aPrice1, bPrice2, aPrice2, lPrice1, lPrice2;
    int64_t time1, time2;
    PosStatus status;
    ActionSide side;
    int32_t iniLot;
    int chaoP1, chaoP2;
    // onOrder1
    int gfd1, gfd2, fak1, fak2, fok1, fok2;
    int64_t orderData;
    int64_t startPairCounter = 0;
    std::vector<int32_t> finishFlags1;
    std::vector<int32_t> finishFlags2;
    uint64_t finishOffset1 = 0;
    uint64_t finishOffset2 = 0;
    uint64_t openOffset1 = 0;
    uint64_t openOffset2 = 0;
    int64_t openOffsetLot1 = 0;
    int64_t openOffsetLot2 = 0;

public:
    PairTrader() //构造函数
    {
        //合约ID
        ticker1 = TickerID("cu2203.SHFE");
        ticker2 = TickerID("cu2204.SHFE");
        //取得快照地址
        using namespace std::placeholders;
        qoute1 = (sci::RingBufferX *)drive->use_event<SS::QuoteEvent>()->get_para_addr(ticker1, sci::MDX_Moff::quote_buffer);
        qoute2 = (sci::RingBufferX *)drive->use_event<SS::QuoteEvent>()->get_para_addr(ticker2, sci::MDX_Moff::quote_buffer);
    }

    void TickHis() //盘前计算
    {
        int sum1, sum2;
        int sprAskP[1000], sprBidP[1000];
        for (int i = 0; i < 1000; i += 2)
        {
            sprAskP[i] = q1AskP[i] - q2AskP[i];
            sprBidP[i] = q1BidP[i] - q2BidP[i];
            sum1 += sprAskP[i];
            sum2 += sprBidP[i];
        };
        double averSprAsk = sum1 / 1000;
        double averSprBid = sum2 / 1000;
    }

    int onTick(TickerID ticker, int64_t pos) //盘中计算
    {
        sci::StaticExtraData staticData;
        tick_size = staticData.tick_size;
        bool cancelFlag = false;
        //行情接收处理顺序
        if (ticker == ticker1)
        {
            // quote1盘口数据--q1
            auto q1 = *(qoute1->get<1>(pos));
            aPrice1 = q1.level[0].ask_price;
            bPrice1 = q1.level[0].bid_price;
            lPrice1 = q1.last_price;
            time1 = q1.time;

            for (auto i = finishOffset1; i < orderIds1.size(); ++i)
            {
                using namespace trader;
                Order ord = SS::env::trader->query_order_static(orderIds1[i]).value();
                if (ord.side == SideType::BUY)
                {
                    if (ord.price <= aPrice1 - 2 * tick_size)
                    {
                        CancelOrder canOrd;
                        canOrd.order_id = ord.order_id;
                        SS::env::trader->cancel_order(canOrd);
                        cancelFlag = true;
                    }
                }
                else if (ord.side == SideType::SELL)
                {
                    if (ord.price >= bPrice1 + 2 * tick_size)
                    {
                        CancelOrder canOrd;
                        canOrd.order_id = ord.order_id;
                        SS::env::trader->cancel_order(canOrd);
                        cancelFlag = true;
                    }
                }
            }
        }
        else if (ticker == ticker2)
        {
            // quote2盘口数据--q1
            auto q2 = *(qoute2->get<1>(pos));
            bPrice2 = q2.level[0].bid_price;
            aPrice2 = q2.level[0].ask_price;
            lPrice2 = q2.last_price;
            time2 = q2.time;
        }
        else
        { // error
            exit(0);
        }

        if (std::abs(time1 - time2) < 100 * 1000 * 1000) // 100ms
        {
            // //更新aver
            // double averSprAskLa = (averSprAsk * 0.999 + (q1.last_price - q2.last_price) * 0.001) / 1000;
            // double averSprBidLa = (averSprAsk * 0.999 + (q1.last_price - q2.last_price) * 0.001) / 1000;
            averSprAsk = 0.005 * (lPrice1 - lPrice2) + 0.995 * averSprAsk;
            averSprBid = 0.005 * (lPrice1 - lPrice2) + 0.995 * averSprBid;

            TrigOp1 = floor(averSprAsk - OverP1);
            TrigClo1 = floor(averSprAsk + OverP1);
            TrigOp2 = ceil(averSprBid + OverP2);
            TrigClo2 = ceil(averSprBid - OverP2); // tick_size 倍数

            // int IndiDuo =  int(averSprAsk + 2 * tick_size);
            // int IndiKong =  int(averSprBid + 2 * tick_size);

            // if ((q1.level[0].ask_price - q2.level[0].ask_price) > IndiKong)
            // {
            //     this->handOrder();
            //     int64_t oid, oid1;
            //     int64_t quantity;
            //     double insPrice1, insPrice2;
            //     oid = insertOrder(ticker1, quantity, insPrice1, "pingduo");
            //     using namespace trader;

            //     OrderStatus status = std::get<3>(SS::env::trader->query_order(oid));//返回4个结构体序列
            //     OrderTrader orTrader = std::get<2>(SS::env::trader->query_order(oid));//返回4个结构体序列

            //     if (status.status = OrderStatusType::NO_TRADE_QUEUEING & q1.level[0].bid_price > insPrice1 + 2 * tick_size)
            //     {
            //         //订单无成交
            //         this->cancOrder(ticker1, quantity, insPrice1, oid);
            //     }
            //     else if (status.status == OrderStatusType::PART_TRADED_QUEUEING)
            //     {
            //             oid1 = insertOrder(ticker2, status.quantity_traded, insPrice2, "pingduo");
            //             OrderTrader orTrader = std::get<2>(SS::env::trader->query_order(oid));//返回4个结构体序列

            //             double LaProfit1 = (orTrader.price - insPrice1) * 5 - status.handling_fee
            //             double LaProfit2 = (orTrader.price - insPrice2) * 5 - status.handling_fee
            //             double LaProfit = LaProfit1 + LaProfit1;

            //             this->PosModify(LaProfit, oid, oid1, quantity, status.quantity_traded);
            //     }
            //     else if (status.status == OrderStatusType::ALL_TRADED)
            //     {
            //             oid = insertOrder(ticker1, status.quantity_traded, insPrice1, "pingduo");
            //             OrderTrader orTrader = std::get<2>(SS::env::trader->query_order(oid));//返回4个结构体序列

            //             double LaProfit1 = (orTrader.price - insPrice1) * 5 - status.handling_fee
            //             double LaProfit2 = (orTrader.price - insPrice2) * 5 - status.handling_fee
            //             double LaProfit = LaProfit1 + LaProfit1;

            //             this->PosModify(LaProfit, oid, oid1, quantity, status.quantity_traded);
            //     }
            //     //开启一轮交易on_order
            //     if (oid1  <= 0)
            //     {
            //         exit(oid1);
            //     }
            //     else
            //     {
            //     //kaikong
            //     }
            // }
            // else if ((q1.level[0].ask_price - q2.level[0].ask_price) < IndiDuo)
            // {
            //     //pingkong
            // }
            // else if ((q1.level[0].ask_price - q2.level[0].ask_price) < IndiDuo)
            // {
            //     //kaiduo
            // }

            if (aPrice1 - aPrice2 <= TrigOp1 || (aPrice1 - aPrice2 <= TrigClo2 && aPrice1 - aPrice2 >= TrigOp1))
            {
                side = ActionSide::Long; //正套
            }
            else if (bPrice1 - bPrice2 >= TrigOp2 || (bPrice1 - bPrice2 >= TrigOp1 && bPrice1 - bPrice2 <= TrigOp2))
            {
                side = ActionSide::Short;
            }
            else
            {
                side = ActionSide::Empty;
            }

            if (cancelFlag)
            {
                ++startPairCounter;
            }
            else
            {
                startPair(++startPairCounter);
            }
        }
        else
        {
            std::cout << "q1, q2行情不同步" << std::endl;
        }
        return 0;
    }

    void setOrderData(uint64_t data)
    {
        orderData = data;
    }

    int startPair(uint64_t spc) // send ticker1
    {
        if (spc < startPairCounter)
        {
            return 0;
        }
        if (status < PosStatus::LongPartialLong && finishOffset1 == orderIds1.size() && finishOffset2 == orderIds2.size())
        {
            using namespace trader;
            Order ord;
            ord.ticker = ticker1;
            ord.price_type = PriceType::LIMIT;
            switch (side)
            {
            case ActionSide::Long:
            {
                ord.side = SideType::BUY;
                ord.price = aPrice1 - chaoP1 * tick_size;
                if (SPosHis1 > 0)
                {
                    ord.offset = OffsetType::CLOSE_YESTERDAY;
                    ord.quantity = iniLot > SPosHis1 ? SPosHis1 : iniLot;
                }
                else if (SPosTod1 > 0)
                {
                    ord.offset = OffsetType::CLOSE_TODAY;
                    ord.quantity = iniLot > SPosTod1 ? SPosTod1 : iniLot;
                }
                else
                {
                    ord.offset = OffsetType::OPEN;
                    ord.quantity = iniLot;
                }
                break;
            }
            case ActionSide::Short:
            {
                ord.side = SideType::SELL;
                ord.price = bPrice1 + chaoP1 * tick_size;
                if (LPosHis1 > 0)
                {
                    ord.offset = OffsetType::CLOSE_YESTERDAY;
                    ord.quantity = iniLot > LPosHis1 ? LPosHis1 : iniLot;
                }
                else if (LPosTod1 > 0)
                {
                    ord.offset = OffsetType::CLOSE_TODAY;
                    ord.quantity = iniLot > LPosTod1 ? LPosTod1 : iniLot;
                }
                else
                {
                    ord.offset = OffsetType::OPEN;
                    ord.quantity = iniLot;
                }
                break;
            }
            case ActionSide::Empty:
            {
                return 0;
            }
            }
            auto ordId = SS::env::trader->insert_order(ord); //下一tick撤单
            if (ordId <= 0)
            {
                exit(ordId);
            }
            orderIds1.push_back(ordId);
            // gfd1 += 1;
            finishFlags1.push_back(false);
            offsets.push_back(orderIds2.size());
            return 0;
        }
        else
        {
            using namespace std::chrono_literals;
            drive->use_event<SS::TimerEvent>()->add_for(50ms, [this, spc]()
                                                        { return this->startPair(spc); });
        }
    }

    int onOrder(const trader::OrderRes &ordRes, const trader::Order &ord)
    {
        using namespace trader;
        if (ord.ticker == ticker1)
        {
            if (ordRes.quantity > 0)
            {
                Order ord1;
                if (ordRes.side == SideType::BUY)
                {
                    switch (ordRes.offset)
                    {
                    case OffsetType::CLOSE_YESTERDAY:
                    {
                        SPosHis1 -= ordRes.quantity;
                        status = PosStatus::ShortPartialLong;
                        break;
                    }
                    case OffsetType::CLOSE_TODAY:
                    {
                        SPosTod1 -= ordRes.quantity;
                        status = PosStatus::ShortPartialLong;
                        break;
                    }
                    case OffsetType::OPEN:
                    {
                        LPosTod1 += ordRes.quantity;
                        status = PosStatus::LongPartialLong;
                    }
                    }
                    ord1.side = SideType::SELL;
                    ord1.price = aPrice1 - chaoP1 * tick_size;
                }
                else if (ordRes.side == SideType::SELL)
                {
                    switch (ordRes.offset)
                    {
                    case OffsetType::CLOSE_YESTERDAY:
                    {
                        LPosHis1 -= ordRes.quantity;
                        status = PosStatus::LongPartialShort;
                        break;
                    }
                    case OffsetType::CLOSE_TODAY:
                    {
                        LPosTod1 -= ordRes.quantity;
                        status = PosStatus::LongPartialShort;
                        break;
                    }
                    case OffsetType::OPEN:
                    {
                        SPosTod2 += ordRes.quantity;
                        status = PosStatus::ShortPartialShort;
                    }
                    }
                    ord1.side = SideType::BUY;
                    ord1.price = bPrice1 + chaoP1 * tick_size;
                }
                ord1.data = orderData + orderIds2.size();
                ord1.ticker = ticker2;
                ord1.price_type = PriceType::FAK;
                ord1.offset = ord.offset;
                ord1.quantity = ordRes.quantity;
                auto oid2 = SS::env::trader->insert_order(ord1);
                if (oid2 <= 0)
                {
                    exit(0);
                }                
                orderIds2.push_back(oid2);
                finishFlags2.push_back(false);
                closeProfit2.push_back(0);
            } //订单次数统计
            if (ordRes.is_finally())
            {
                auto idIndex = ord.data - orderData;
                finishFlags1[idIndex] = true;
                while (finishOffset1 < finishFlags1.size() && finishFlags1[finishOffset1])
                {
                    finishOffset1++;
                }

                // if (ordRes.offset != OffsetType::OPEN)//盈亏计算
                // {
                //     double matchAmount = 0;
                //     double matchFee = 0;
                    
                //     OrderStatus ordSts = SS::env::trader->query_order_status(ordRes.order_id).value();
                //     int64_t q = ordSts.quantity_traded;

                //     OrderStatus ordSri = SS::env::trader->query_order_status(orderIds1[openOffset1]);
                    
                //     while ((q -= (ordSri.quantity_traded - openOffsetLot1)) >= 0)
                //     {
                //         double ratio = 1.0 - ((double)openOffsetLot1 / (double)ordSri.quantity_traded);
                //         matchAmount += ratio * ordSri.total_price;
                //         matchFee += ratio * ordSri.handling_fee;
                //         openOffsetLot1 = 0;
                //         while (SS::env::trader->query_order_static(orderIds1[++openOffsetLot1]).value().offset != OffsetType::OPEN)
                //         {
                //             OrderStatus ordSri = SS::env::trader->query_order_status(orderIds1[openOffsetLot1]]);
                //         }
                //     }
                //     openOffsetLot1 = ordSri.quantity_traded + q;
                //     double ratio = (double)openOffsetLot1 / (double)ordSri.quantity_traded;
                //     matchAmount += ratio * ordSri.total_price;
                //     matchFee += ratio * ordSri.handling_fee;
                //     closeProfit1[idIndex]  = ordSts.total_price - matchAmount - matchFee - ordSts.handling_fee;
                // }
            }
        }
        else if (ord.ticker == ticker2)
        {
            if (ordRes.quantity > 0)
            {
                if (ordRes.side == SideType::SELL)
                {
                    switch (ordRes.offset)
                    {
                    case OffsetType::CLOSE_YESTERDAY:
                    {
                        LPosHis2 -= ordRes.quantity;
                        auto longPos = LPosHis2 + LPosTod2;
                        if (longPos == (SPosHis1 + SPosTod1))
                        {
                            status = longPos > 0 ? PosStatus::Short : PosStatus::Empty;
                        }
                        break;
                    }
                    case OffsetType::CLOSE_TODAY:
                    {
                        LPosTod2 -= ordRes.quantity;
                        auto longPos = LPosHis2 + LPosTod2;
                        if (longPos == (SPosHis1 + SPosTod1))
                        {
                            status = longPos > 0 ? PosStatus::Short : PosStatus::Empty;
                        }
                        break;
                    }
                    case OffsetType::OPEN:
                    {
                        SPosTod2 += ordRes.quantity;
                        auto shortPos = SPosHis1 + SPosTod1;
                        if (shortPos == (LPosHis1 + LPosTod1))
                        {
                            status = PosStatus::Long;
                        }
                    }
                    }
                }
                else if (ordRes.side == SideType::BUY)
                {
                    switch (ordRes.offset)
                    {
                    case OffsetType::CLOSE_YESTERDAY:
                    {
                        SPosHis2 -= ordRes.quantity;
                        auto shortPos = SPosHis2 + SPosTod2;
                        if (shortPos == (LPosHis1 + LPosTod1))
                        {
                            status = shortPos > 0 ? PosStatus::Long : PosStatus::Empty;
                        }
                        break;
                    }
                    case OffsetType::CLOSE_TODAY:
                    {
                        SPosTod2 -= ordRes.quantity;
                        auto shortPos = SPosHis2 + SPosTod2;
                        if (shortPos == (LPosHis1 + LPosTod1))
                        {
                            status = shortPos > 0 ? PosStatus::Long : PosStatus::Empty;
                        }
                        break;
                    }
                    case OffsetType::OPEN:
                    {
                        LPosTod1 += ordRes.quantity;
                        auto longPos = LPosHis2 + LPosTod2;
                        if (longPos == (SPosHis1 + SPosTod1))
                        {
                            status = PosStatus::Short;
                        }
                    }
                    }
                }
            } //次数统计
            if (ordRes.is_finally())
            {
                auto idIndex = ord.data - orderData;
                finishFlags2[idIndex] = true;
                while (finishOffset2 < finishFlags2.size() && finishFlags2[finishOffset2])
                {
                    finishOffset2++;
                }

                OrderStatus osts = SS::env::trader->query_order_status(ordRes.order_id).value();//undefined reference to `StrategySystem::TraderApi::query_order_status(unsigned int)'

                auto qLeft = ord.quantity - osts.quantity_traded;
                if (qLeft > 0)
                {
                    Order ord2(ord); //??
                    ord2.data = orderData + orderIds2.size();
                    ord2.quantity = qLeft;
                    auto oid2 = SS::env::trader->insert_order(ord2);
                    if (oid2 <= 0)
                    {
                        exit(oid2);
                    }
                    orderIds2.push_back(oid2);
                    finishFlags2.push_back(false);
                    closeProfit2.push_back(0);
                }
                else
                {
                    using namespace std::chrono_literals;
                    drive->use_event<SS::TimerEvent>()->add_for(50ms, [this, spc = this->startPairCounter]()
                                                                { return this->startPair(spc); });
                }
            }
        }
        else
        {
            exit(ord.order_id); // error!
        }
    }

    void onCancel(const trader::CancelRes &res, const trader::Order &ord){

    }

    // int onorder(const trader::OrderRes& ordRes,const trader::Order& ord) //tick内补全B合约
    // {
    //     int64_t oid1, oid2;
    //     int TradedLot;
    //     using namespace trader;
    //     if (ord.ticker == ticker1)
    //     {
    //         if (ordRes.quantity > 0)
    //         {
    //             Order ord2;
    //             ord2.ticker = ticker2;

    //             if (ordRes.offset == OffsetType::CLOSE_TODAY)
    //             {
    //                 ordRes.price
    //             }
    //             else
    //             {}
    //             ord2.offset = ordRes.offset;
    //             ord2.quantity = ordRes.quantity;
    //             ord2.price_type = FAK;  //??
    //             if (ordRes.side == SideType::BUY)
    //             {
    //                 ord2.side = SideType::SELL;
    //                 ord2.price = aPrice2 - chaoP2 * tick_size;
    //             }
    //             else
    //             {
    //                 ord2.side = SideType::BUY;
    //                 ord2.price = bPrice2 - chaoP2 * tick_size;
    //             }
    //             auto ordId2 = SS::env::trader->insert_order(ord2);
    //             oid2 = ordId2
    //             if (oid2 <= 0)
    //             {
    //                 exit(ordId);
    //             }
    //             orderIds2.push_back(oid2);
    //             fak2 += 1;
    //         }
    //         else
    //         {
    //             //继续等待成交
    //         }

    //         TradedLot = ordRes.quantity; //A成交的数量
    //     }
    //     else if (OrderRes.order_id = oid2)
    //     {
    //         if (ordRes.quantity < TradedLot)
    //         {   //再次FAK报单
    //             Order ord3;
    //             ord3.ticker = ticker2;
    //             ord3.offset = ordRes.offset;
    //             ord3.quantity = TradedLot - ordRes.quantity;
    //             ord3.price_type = FAK;
    //             ord3.side = ordRes.side;
    //             if (ordRes.side == SideType::SELL)
    //             {
    //                 ord2.side = SideType::SELL;
    //                 ord2.price = aPrice2 - chaoP2 * tick_size;
    //             }
    //             else
    //             {
    //                 ord2.side = SideType::BUY;
    //                 ord2.price = bPrice2 - chaoP2 * tick_size;
    //             }

    //             auto ordId3 = SS::env::trader->insert_order(ord3);
    //             fak2 += 1;
    //         }
    //         else
    //         {   //全部成交，配对完成

    //         }
    //     }
    //     return 0;
    // }

    // trader::Position  getPostion(TickerID ticker)
    // {
    //     using namespace trader;
    //     auto dy = SS::env::trader->query_ticker_dynamic(ticker1);

    //     if(dy != nullptr)
    //     {
    //         Position posSToday = SS::env::trader->query_ticker_dynamic(ticker)->get_position(PositionType::SHORT_TODAYA);
    //         Position posSHis = SS::env::trader->query_ticker_dynamic(ticker)->get_position(PositionType::SHORT_YESTERDAY);
    //         std::tuple<struct trader::Position, int32_t> pos (posLToday, posLHis, posSToday, posSHis, posL, posS);

    //         int posL = posLToday.al;
    //         int posS = posSHis.all +posSToday.all;

    //         if (posL > 0 && posS == 0)
    //         {
    //             //A有多头
    //         }
    //         else if (posL == 0 && posS > 0)
    //         {
    //             //A有空头
    //         }
    //         else if (posL > 0 && posS > 0 && posL == posS)
    //         {
    //             //A多空数量相等
    //         }
    //         else if (posL == 0 && posS == 0)
    //         {
    //             //A无持仓
    //         }
    //     }
    //     else
    //     {
    //         //肯定没有持仓
    //     }
    //    return pos;
    // }

    // int64_t posCheck(TickerID ticker1, TickerID ticker2)
    // {
    //     using namespace trader;
    //     auto dy = SS::env::trader->query_ticker_dynamic(ticker1);

    //     if(dy != nullptr)
    //     {
    //         //有可能有持仓
    //         // if(dy->get_position(PriceType))
    //         trader::Position posLToday1, posLHis1, posSToday1, posSHis1 = getPostion(ticker1);
    //         trader::Position posLToday2, posLHis2, posSToday2, posSHis2 = getPostion(ticker1);

    //         int32_t posL1 = posLToday1.all + posLHis1.all; //总多头
    //         int32_t posS1 = posLToday1.all + posLHis1.all; //总多头

    //         int32_t posL2 = posSToday2.all + posSHis2.all; //总空头
    //         int32_t posS2 = posSToday2.all + posSHis2.all; //总空头

    //         if (posL1 > 0 && posS1 == 0)
    //         {
    //             //A有多头
    //             if (posL2 == 0 && posS2 == 0)
    //             {
    //                 //A有多头，B无持仓
    //             }
    //             else if (posL2 > 0 && posS2 == 0)
    //             {
    //                 //AB都有多头
    //             }
    //             else if (posL2 == 0 && posS2 > 0 && posS2 == posL2)
    //             {
    //                 //AB正套持仓
    //             }
    //             else if (posL2 > 0 && posS2 > 0 && posL2 == posS2)
    //             {
    //                 //B多空数量对等
    //             }
    //         }
    //         else if (posL1 == 0 && posS1 > 0)
    //         {
    //             //A有空头
    //             if (posL2 == 0 && posS2 == 0)
    //             {
    //                 //A空头，B无持仓
    //             }
    //             else if (posL2 > 0 && posS2 == 0 && posS1 == posL2)
    //             {
    //                 //AB反套持仓
    //             }
    //             else if (posL2 == 0 && posS2 > 0)
    //             {
    //                 //AB同为DuShuai空头
    //             }
    //             else if (posL2 > 0 && posS2 > 0 && posL2 == posS2)
    //             {
    //                 //B多空数量对等
    //             }
    //         }
    //         else if (posL1 > 0 && posS1 > 0 && posL1 == posS1)
    //         {
    //             if (posL2 == 0 && posS2 == 0)
    //             {
    //                 //A多空对等，B无持仓r{
    //                 //A多空对等，B有多单
    //                                                           // if (ord.side == SideType::BUY)
    //                     // {
    //                     // ord2.side = SideType::SELL;
    //                     // ord2.price = aPrice2 - chaoP2 * tick_size;
    //                     // }
    //                     // else
    //                     // {
    //                     //     ord2.side = SideType::BUY;
    //                     //     ord2.price = bPrice2 - chaoP2 * tick_size;
    //                     // }
    //             }
    //             else if  (posL2 == 0 && posS2 > 0 && posS1 == posS2)
    //             {
    //                 //AB多空对等，B有空单
    //             }
    //             else if (posL2 > 0 && posS2 > 0 && posL2 == posS2)
    //             {
    //                 //B多空数量对等
    //             }
    //         }
    //         else if (posL1 == 0 && posS1 == 0)
    //         {
    //             //A无持仓
    //             if (posL2 == 0 && posS2 == 0)
    //             {
    //                 //AB无持仓
    //             }
    //             else if (posS2 > 0 && porsL2 ==0)
    //             {
    //                 //B有多头
    //             }
    //             else if (posL2 == 0 && posS2 > 0)
    //             {
    //                 //B有空头
    //             }
    //             else if (posL2 > 0 && posS2 > 0 && posL2 == posS2)
    //             {
    //                 //B多空数量对等
    //             }
    //         }
    //     }
    //     else
    //     {
    //         //肯定没有持仓
    //     }
    // }

    // int64_t cancOrder(TickerID ticker, int quantity, int price, int64_t order_id)
    // {

    //     using namespace trader;

    //     CancelOrder cancorder;
    //     CancelStatus status;
    //     unit16_t user_id;
    //     unit64_t user_virtual;
    //     std::chrono::nanoseconds time;

    //     cancorder.user_id = user_id;
    //     cancorder.order_id = order_id;
    //     cancorder.user_virtual = user_virtual;
    //     cancorder.time = time;

    //     int64_t cancOId = SS::env::trader->cancel_order(cancorder);
    //     // order.time = ordTime;

    //     if (status.status = OrderStatusType::CANCELED)
    //     {
    //         std::cout << "撤单成功" << std::endl;
    //     }
    //     else if (status.status = OrderStatusType::RISK || OrderStatusType::REJECTED)
    //     {
    //         std::cout << "撤单失败" << std::endl;
    //     }
    // }

    // int64_t insertOrder(TickerID ticker, int quantity, int price, std::string kaiping = "")
    // {
    //     int64_t oid; //订单id
    //     using namespace trader;r

    //     trader::Position posLToday, posLHis, posSToday, posLhis = getPostion(ticker);

    //     if (kaiping == "kaiduo")
    //     {
    //         Order ord;
    //         ord.side = SideType::BUY;
    //         ord.offset = OffsetType::OPEN;
    //         ord.ticker = ticker;
    //         ord.quantity = quantity;
    //         ord.price_type = PriceType::LIMIT; //限价单
    //         ord.price = price;

    //         oid = SS::env::trader->insert_order(ord);
    //     }
    //     else if (kaiping == "kaikong")
    //     {
    //         Order ord;
    //         ord.side = SideType::SELL;
    //         ord.offset = OffsetType::OPEN;
    //         ord.ticker = ticker;
    //         ord.quantity = quantity;
    //         ord.price_type = PriceType::LIMIT;
    //         ord.price = price;

    //         oid = SS::env::trader->insert_order(ord);
    //     }
    //     else if (kaiping == "pingduo")
    //     {
    //         if (posLToday.all = 0)
    //         {
    //             Order ord = {};
    //             ord.side = SideType::SELL;
    //             ord.offset = OffsetType::CLOSE_YESTERDAY;
    //             ord.ticker = ticker;
    //             ord.quantity = quantity;
    //             ord.price_type = PriceType::LIMIT;
    //             ord.price = price;

    //             oid = SS::env::trader->insert_order(ord);
    //         }
    //         else if (posLHis.all = 0)
    //         {
    //             Order ord;
    //             ord.side = SideType::SELL;
    //             ord.offset = OffsetType::CLOSE_TODAY;
    //             ord.ticker = ticker;
    //             ord.quantity = quantity;
    //             ord.price_type = PriceType::LIMIT;
    //             ord.price = price;

    //             oid = SS::env::trader->insert_order(ord);
    //         }
    //         else
    //         {
    //             Order ord;
    //             ord.side = SideType::SELL;
    //             ord.offset = OffsetType::CLOSE_YESTERDAY;
    //             ord.ticker = ticker;
    //             ord.quaSS::env::trader->on_order(std::bind(&Signal::on_order, this, _1));

    //             ord.quantity = quantity;
    //             ord.price_type = PriceType::LIMIT;
    //             ord.price = price;

    //             oid = SS::env::trader->insert_order(ord);
    //         }
    //         if (posSToday.all = 0)
    //         {
    //             Order ord;
    //             ord.side = SideType::BUY;
    //             ord.offset = OffsetType::CLOSE_YESTERDAY;
    //             ord.ticker = ticker;
    //             ord.quantity = quantity;
    //             ord.price_type = PriceType::LIMIT;
    //             ord.price = price;

    //             oid = SS::env::trader->insert_order(ord);
    //         }
    //         else if (posSHis.all = 0)
    //         {
    //             Order ord;
    //             ord.side = SideType::BUY;
    //             ord.offset = OffsetType::CLOSE_TODAY;
    //             ord.ticker = ticker;
    //             ord.quantity = quantity;
    //             ord.price_type = PriceType::LIMIT;
    //             ord.price = price;

    //             oid = SS::env::trader->insert_order(ord);
    //         }
    //         else
    //         {
    //             Order ord;
    //             ord.side = SideType::BUY;
    //             ord.offset = OffsetType::CLOSE_YESTERDAY;
    //             ord.ticker = ticker;
    //             ord.quantity = quantity;
    //             ord.price_type = PriceType::LIMIT;
    //             or d.price = price;
    //             Order ord;
    //             ord.side = SideType::BUY;
    //             ord.offset = OffsetType::CLOSE_TODAY;
    //             ord.ticker = ticker;
    //             ord.quantity = quantity;
    //             ord.price_type = PriceType::LIMIT;
    //             ord.price = price;

    //             oid = SS::env::trader->insert_order(ord);
    //         }
    //     }
    //     return 0;
    // }

    // int64_t PosModify(double laProfit, int64_t oid1, int64_t oid2, int64_t laCloLot, int64_t laOpLot)
    // {
    //     using namespace trader;
    //     if (laProfit < 0)
    //     {
    //         laCloLot *= 2;
    //     }
    //     else if (laProfit > 0)
    //     {

    //     }
    //     return laCloLot, laOpLot;
    // }

    ~PairTrader() = default;
};

class OrderInfoRouter
{
private:
    std::vector<std::shared_ptr<PairTrader>> traders;
    const uint32_t lShift;

public:
    OrderInfoRouter(uint32_t lsft = 56) : lShift(lsft) {}

    int routeRegister(const std::shared_ptr<PairTrader> &trader)
    {
        traders.push_back(trader);
        trader->setOrderData(uint64_t(traders.size() - 1) << lShift);
    }

    int onOrder(const std::variant<trader::OrderRes, trader::CancelRes> &res)
    {
        using namespace trader;
        std::visit([&](auto &&arg)
        {
            using T = std::decay_t<decltype(arg)>;
            if constexpr (std::is_same_v<T, OrderRes>)
            {
                Order ord = SS::env::trader->query_order_static(arg.order_id).value();
                traders[ord.data >> lShift]->onOrder(arg, ord);
            }
            else if constexpr (std::is_same_v<T, CancelRes>)
            {
                Order ord = SS::env::trader->query_order_static(arg.order_id).value();
                traders[ord.data >> lShift]->onCancel(arg, ord);
            } // else static_assert(always_false_v<T>, "non-exhaustive visitor!"); },        
        }, res);

        return 0;
    }
};

//主线程
extern "C"
{
    int strategy_start(int argc, char **argv)
    {
        using namespace std::placeholders;
        using namespace std::chrono_literals;
        drive = SS::env::drive<drive_t>;
        //创建行情事件实例
        auto trader1 = std::make_shared<PairTrader>();
        auto sm = std::make_shared<SS::SignalManager>();
        sm->add_signal("pairTrader1", [&trader1](TickerID ticker, int64_t type, int64_t pos) -> bool
                       {
                           return trader1->onTick(ticker, pos);
                        });
        auto qoute = drive->use_event<SS::QuoteEvent>();
        qoute->sub_snapshot(TickerID("cu2203.SHFE"), sm);
        qoute->sub_snapshot(TickerID("cu2204.SHFE"), sm);
        auto oir = std::make_unique<OrderInfoRouter>();
        oir->routeRegister(trader1);
        SS::env::trader->on_order([&oir](const std::variant<trader::OrderRes, trader::CancelRes> &res)
                                  { return oir->onOrder(res); }); //订单回报处理
        return 0;
    }

    //策略退出
    int strategy_exit(int code)
    {
        std::cout << "exit" << std::endl;
        return 0;
    }

    //策略异常
    int strategy_error(int code)
    {
        return 0;
    }

    extern int strategy_main(int argc, char **argv);
}

int main(int argc, char **argv)
{
    //策略管理
    return strategy_main(argc, argv);
}