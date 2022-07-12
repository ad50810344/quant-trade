#include <iostream>
#include <fstream>
#include <ostream>
#include <vector>
#include <variant>
#include <json/json.h>
#include <time.h>
#include "env.hpp"
#include "drive.hpp"
#include "quote_event.hpp"
#include "timer_event.hpp"
#include "trader_api.hpp"
#include <math.h>
#include <filesystem>
#include "config_monitor.hpp"
#include <algorithm>
#include <string>
//0614 价差波段交易
/*
    输入参数：
        合约代码    TickerID ticker1, ticker2
        tick大小    double tick_size1、tickz_size2
        历史价差均值  double aSprAver, bSprAver
        价差标准差    double stdA, stdB
        撤单限制    int cancelLimit1, cancelLimt2
        策略持仓    int strategyPosition
        最大持仓    int maxPosition
        初始手数    int initLot
        最大手数    int maxLot
        循环次数    int loopCount
        循环间隔    int loopInterval
        合约乘数    int contractMultil, contractMulte2
        距离停板价格    int stopLimitPrice
        策略资金比例 int strategyCapiRatio
        超价        int overPrice1, overPriceA, overPriceB
        保证金比例   double marginRatio1, marginRatio2
    
    中间参数：
        行情地址    quote1, quote2
        订单地址    unit64_t orderData
        配对开关    unite32_t startPairCouter
        持仓状态    struct PosStatus
        触发方向    struct ActionSide
                   unit64_t startPairCouter
        订单量长度    vector orderIds1, orderIds2
        订单完成标志    vector finishFlag1, finishFlag2
        平仓盈亏    vector closeProfit1, closeProfit2, pairProfits
        B腿对应位置     vector offsets
        订单回报状态    struct OrderStatus1,OrderStatus2
        子回报位置  unit64_t finishOffset1, finishOffset2      
        持仓数量 int32_t longPositionToday1,2 longPositionHis1,2 shortPositionToday1,2 shortPositionHis1,2
    
        触发开仓    double trigOpen1,trigOpen2
        触发平仓    double trigClose1, trigClose2

        手数        int32_t quantity
        初始手数    int inilot, lotClose
        报单手数    int lot[10]
        一阶步长,二阶步长    int posStep[10], posStep[2]
        统计总手数  int sumLot
        总保证金    double margin
        总权益      double asset1
        单手保证金   symbolMargin

        盘口数据    double bPrice1, aPrice1,bPrice2, aPrice2, lPrice1, lPrice2
        数据时间    time1, time2
        成交总额    double amout1, amount2
        tick均价    double LTickAver
        成交量      int64_t volume1, volume2
        今日成交总量    double amount1Tod, amount2Tdo

        订单数量    int ordNum1, ordNum2
        未滑点订单量   int noslipped1, noslipped2
        滑点订单量  int slipped1, slipped2
        撤单次数    int cancl1Count, cancl2Count
        利润率      double ratioOfProfit
        利润        double Profit
        持有时间    double timeOfHold
        

    输出参数：       eg
        期货账号    000000          char account
        策略编号    1               int strategyCode
        合约代码    cu2205,cu2204   char ticker1
        策略开关    true            bool strategyActivate
        信号开关    true            bool singleActivate
        单策略分配资金  500000       double strategyCapital
        单策略持仓资金  300000       double strategyCapitalUsed
        分配仓位    20              int allowedPosition
        总持仓      16              int Position
        买持仓      16              int longPosition
        卖持仓      0               int shortPosition
        买价        -10             bouble spreadBidPrice
        卖价        20              double spreadAskPrice
        持仓盈亏    1000             double holdProfits
        平仓盈亏    2000             double closedProfits
        手续费      1300            double fee
        净盈亏      700             double netProfit
        A成家率     0.27            double tradedRatioA
        B成交率     0.90            double tradedRatioB
        撤单统计    350/350         int canceledNumberA
        撤单限制    450/450         int calcelLimit
        超价触发    2/2/0           int overPirce
        A时效       GFD             char timeConditionA
        AFAK次数    10000           int AFAK
        成交量      3000            int amount
        成交额      210000          int turnOver
        BFAK次数    60000           int BFAK
*/

using namespace std;
namespace SS = StrategySystem;
using drive_t = SS::Drive<SS::QuoteEvent, SS::TimerEvent, SS::TraderApi>;
drive_t *drive;

struct PairTraderConfig {
    // true = startPair(), false = return 0
    bool running;
    int initLot;
    double strategyCapiRatio;
    int overPri1 = 2, overPriceA = 2, overPriceB = 0;
    int cancelBuyA, cancelSellA, cancelBuyB, cancelSellB, cancelSellBClose, cancelBuyBClose;
    int sendBuyA, sendSellA, sendBuyB, sendSellB;
    int stoplossTick;
    int downOpenLong, upOpenShort, downCloShort, upCloLong;


    PairTraderConfig& operator=(const Json::Value& val) {
        // std::cout << __LINE__ << std::endl;
        running = val["running"].asBool();
        initLot = val["initLot"].asInt();
        strategyCapiRatio = val["strategyCapiRatio"].asDouble();
        overPri1 = val["overPrice1"].asInt();
        overPriceA = val["overPriceA"].asInt();
        overPriceB = val["overPriceB"].asInt();

        cancelBuyA = val["cancelBuyA"].asInt();
        cancelSellA = val["cancelSellA"].asInt();
        cancelBuyB = val["cancelBuyB"].asInt();
        cancelSellB = val["cancelSellB"].asInt();
        cancelSellBClose = val["cancelSellBClose"].asInt();
        cancelBuyBClose = val["cancelBuyBClose"].asInt();

        sendBuyA = val["sendBuyA"].asInt();
        sendSellA = val["sendSellA"].asInt();
        sendBuyB = val["sendBuyB"].asInt();
        sendSellB = val["sendSellB"].asInt();

        stoplossTick = val["stoplossTick"].asInt();

        downOpenLong = val["downOpenLong"].asInt();
        upOpenShort = val["upOpenShort"].asInt();
        downCloShort = val["downCloShort"].asInt();
        upCloLong = val["upCloLong"].asInt();
        return *this;
    }
};

SS::ConfigMonitor<PairTraderConfig> config;

class PairTrader
{
private:
    struct PosStatus {
        enum Value {
            Empty = 0,
            Long = 1,
            Short = 3,
            LongPartialLong = 5,
            ShortPartialLong = 7,
            LongPartialShort = 13,
            ShortPartialShort = 15
        };

        PosStatus(Value v):value(v) {
        }

        bool isEmpty() const {
            return value == 0;
        }

        bool isLong() const {
            return (value & 3) == 1;
        }

        bool isShort() const {
            return (value & 3) == 3;
        }

        bool isBalance() const {
            return value < 5;
        }

        PosStatus& operator=(Value v) {
            value = v;
            return *this;
        }

        Value value = Empty;  
    };

    enum class Action {
        OpenLong,
        OpenShort,
        CloseLong,
        CloseShort,
        Empty
    };

    struct Profit {
        double profit=0;
        double fee=0;
        Profit& operator+=(const Profit& rhs) {
            profit += rhs.profit;
            fee += rhs.fee;
            return *this;
        }
        friend Profit operator+(Profit lhs, const Profit& rhs) {
            lhs += rhs;
            return lhs;
        }
        double netProfit() const {
            return profit - fee;
        }
    };

    const StrategySystem::ConfigMonitor<PairTraderConfig>::Buffer* pRunningConfig;

    bool running = true;
    TickerID ticker1;
    TickerID ticker2;
    double bPrice1, aPrice1, bPrice2, aPrice2, lPrice1, lPrice2;
    int64_t time1, time2;

    uint64_t orderData;
    uint32_t startPairCouter=0;

    sci::RingBufferX *quote1;
    sci::RingBufferX *quote2;
    
    std::vector<int32_t> orderIds1;
    std::vector<int32_t> orderIds2;
    std::vector<bool> finishFlags1;
    std::vector<bool> finishFlags2;
    std::vector<Profit> closeProfits1;
    std::vector<Profit> closeProfits2;
    uint64_t finishOffset1 = 0, finishOffset2 = 0;
    uint64_t openOffset1 = -1, openOffset2 = -1;//-1 start ??
    int64_t openOffsetQuantity1 = 0, openOffsetQuantity2 = 0;
    trader::OrderStatus OrderStatus1;
    trader::OrderStatus OrderStatus2;
    std::vector<uint64_t> offsets;
    std::vector<Profit> pairProfits;
    std::vector<double> nearPairProfits;
    std::vector<double> maPairProfits;

    Profit closeProfit;
    Profit openProfit;
    double avgOpenAmount1 = 0, avgOpenAmount2 = 0;
    double avgOpenFee1 = 0, avgOpenFee2 = 0;
    uint64_t cancelCount1 = 0, cancelCountFak2 = 0, cancelCountLimit2 = 0, reInsertOrderB = 0;
    uint64_t allTradedCount1 = 0, allTradedCount2 = 0;
    double cancelRatio1 = 0, cancelRatio2 = 0;
    uint64_t onPriceCount1 = 0, onPriceCount2 = 0;
    uint64_t betterPriceCount1 = 0, betterPriceCount2 = 0;
    double onPriceRatio1 = 0, onPriceRatio2 = 0;
    uint64_t gainPairCount = 0, lossPairCount = 0;

    double openProfitStopLoss;
    double stopless;

    int32_t  longPositionToday1=0,longPositionHis1=0,shortPositionToday1=0,shortPositionHis1=0;
    int32_t  longPositionToday2=0,longPositionHis2=0,shortPositionToday2=0,shortPositionHis2=0;

    PosStatus status = PosStatus::Empty;
    Action side = Action::Empty;
    int32_t quantity = 0;
    int32_t sumQuantity = 0;
    double price1, price2;
    std::vector<double> ATickSerialAskP;
    std::vector<double> BTickSerialAskP;
    std::vector<double> ATickSerialBidP;
    std::vector<double> BTickSerialBidP;
    std::vector<double> sprAverSerial;
    std::vector<double> closeSpr;
    int sprAver;
    double downOpenLong = 2, upOpenShort = 2, downCloShort = 1, upCloLong = 1;
    

    int inilot, lotClose;       
    int posStep2 = 0, posStep[10], lot[10];   
    int sumLot = 0;           
    double margin;
    double asset1, symbolMargin;
    
    double amount1, amount2, LTickAver;
    int64_t volume1, volume2;
    double amount1Tod, amount2Tod;
    double ratioOfProfit, timeOfHold;


    double tick_size1, tick_size2;
    double aSprAver, bSprAver, stdA, stdB, tickAver;
    double margin1, margin2;
    int cancelLimit1, cancelLimit2;
    int strategyPosition, maxPosition, initLot, maxLot, loopCount, loopInterval;
    int contractMulti1, contractMulti2, stopLimitPrice;
    double strategyCapiRatio;
    int overPriSum, overPriceA, overPriceB;
    double marginRatio1, marginRatio2;
    int position1, position2;
    int loopNum= 0;
    std::vector<std::chrono::nanoseconds> ATime;    //报单时间
    std::vector<std::chrono::nanoseconds> BTime;

    std::unique_ptr<std::fstream> logFile;
    // std::unique_ptr<std::fstream> orderLogFile;
    // std::unique_ptr<std::fstream> tradesLogFile;    
    //盘中实时修改的参数需要分类
    // time_t rawtime;

public:
    PairTrader(const std::filesystem::path& configFile){
        SS::env::LOG(std::cout, std::string_view("初始化pairTrader\n"));
        // **(sci::StaticQuote**)drive->use_event<SS::QuoteEvent>()->get_para_addr(sci::MDX_Moff::pStaticQuote);
        // LoadData("cu2201_20210624.csv");//数据读取
        //12点行情
        //Btui chiyou shijian

        std::ifstream file(configFile.string());
        Json::Value root;
        file >> root;
        auto runningConfigFile = configFile.parent_path() / root.get("runningConfig", "").asString();
        pRunningConfig = config.add_file(runningConfigFile.string());
        ticker1 = TickerID(root.get("ticker1", "").asString());
        ticker2 = TickerID(root.get("ticker2", "").asString());
        quote1 = (sci::RingBufferX *)drive->use_event<SS::QuoteEvent>()->get_para_addr(ticker1, sci::MDX_Moff::quote_buffer);
        quote2 = (sci::RingBufferX *)drive->use_event<SS::QuoteEvent>()->get_para_addr(ticker2, sci::MDX_Moff::quote_buffer);
        tick_size1 = root.get("tick_size1", 0.01).asDouble();
        tick_size2 = root.get("tick_size2", 0.01).asDouble();

        aSprAver = root.get("aSprAver", 0.01).asDouble();
        bSprAver = root.get("bSprAver", 0.01).asDouble(); 

        stdA = root.get("stdA", 0).asDouble();
        stdB = root.get("stdB", 0).asDouble();
        tickAver = root.get("tickAver", 0).asInt();
        margin1 = root.get("margin1", 0).asDouble();
        margin2 = root.get("margin2", 0).asDouble(); 
        cancelLimit1 = root.get("cancelLimit1", 0).asInt();
        cancelLimit2 = root.get("cancelLimit2", 0).asInt();
        strategyPosition = root.get("strategyPosition", 0).asInt();
        maxLot = root.get("maxLot", 0).asInt();
        loopCount = root.get("loopCount",0).asInt();
        loopInterval = root.get("loopInterval",0).asInt();
        overPriSum = root.get("overPrice1",0).asInt();
        overPriceA = root.get("overPriceA",0).asInt();
        overPriceB = root.get("overPriceB",0).asInt();
        contractMulti1 = root.get("contractMulti1",0).asInt();
        contractMulti2 = root.get("contractMulti2",0).asInt();
        stopLimitPrice = root.get("stopLimitPrice",0).asInt();
        strategyCapiRatio = root.get("strategyCapiRatio",0).asDouble();

        // root["aSprAver"] = 100000;
        // Json::StyledWriter sw;
        // ofstream os;
        // int pos1 = configFile.string().find_last_of('/');
        // string js(configFile.string().substr(pos1+1));
        // os.open(js, std::ios::out | std::ios::app);
        // if (!os.is_open()){
        //     std::cout << __LINE__ << "no file to write" << std::endl;
        // }
        // os << sw.write(root);
        // std::cout << __LINE__ << root << std::endl;
        // os.close();

        //json.h bubaoduo
        const Json::Value hos1 = root["hisOrderStatus1"];
        if (hos1.isNull()) {
            OrderStatus1.total_amount = 0;
            OrderStatus1.quantity_traded = 0;
            OrderStatus1.handling_fee = 0;
            OrderStatus1.status = trader::OrderStatusType::CANCELED;
        } else {
            OrderStatus1.total_amount = hos1.get("total_amount", 0).asDouble();
            int64_t volume = hos1.get("total_volume", 0).asInt64();
            if (volume > 0)
            {
                longPositionHis1 = volume;
                OrderStatus1.quantity_traded = volume;
            }
            else
            {
                shortPositionHis1 = -volume;
                OrderStatus1.quantity_traded = -volume;
            }
            OrderStatus1.handling_fee = hos1.get("fee", 0).asDouble();
            OrderStatus1.status = trader::OrderStatusType::ALL_TRADED;
        }
        const Json::Value hos2 = root["hisOrderStatus2"];
        if (hos2.isNull()) {
            OrderStatus2.total_amount = 0;
            OrderStatus2.quantity_traded = 0;
            OrderStatus2.handling_fee = 0;
            OrderStatus2.status = trader::OrderStatusType::CANCELED;
        } else {
            OrderStatus2.total_amount = hos2.get("total_amount", 0).asDouble();
            int64_t volume = hos2.get("total_volume", 0).asInt64();
            if (volume > 0)
            {
                longPositionHis2 = volume;
                OrderStatus2.quantity_traded = volume;
            }
            else
            {
                shortPositionHis2 = -volume;
                OrderStatus2.quantity_traded = -volume;
            }
            OrderStatus2.handling_fee = hos2.get("fee", 0).asDouble();
            OrderStatus2.status = trader::OrderStatusType::ALL_TRADED;
        }
        if (longPositionHis1 > 0 || shortPositionHis2 > 0)
        {
            assert(shortPositionHis1 == 0 && longPositionHis2 == 0);
            if (longPositionHis1 == shortPositionHis2)
            {
                status = PosStatus::Long;
            }
            else if (longPositionHis1 > shortPositionHis2)
            {
                status = PosStatus::LongPartialLong;
            }
            else
            {
                status = PosStatus::LongPartialShort;
            }
        }
        else if (longPositionHis2 > 0 || shortPositionHis1 > 0)
        {
            assert(longPositionHis1 == 0 && shortPositionHis2 == 0);
            if (longPositionHis2 == shortPositionHis1)
            {
                status = PosStatus::Short;
            }
            else if (longPositionHis2 > shortPositionHis1)
            {
                status = PosStatus::ShortPartialShort;
            }
            else
            {
                status = PosStatus::ShortPartialLong;
            }
        }


        logFile = std::make_unique<fstream>(std::string("output/")+root.get("outCsv", "").asString(), std::ios::out | std::ios::in);
        (*logFile) << std::unitbuf;
        SS::env::LOG(*logFile, std::string_view("{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{}\n"), 
        std::string_view("now time"), 
        std::string_view("平仓盈亏"), std::string_view("浮动盈亏"), 
        std::string_view("平仓手续费"), 
        std::string_view("A持仓"), std::string_view("B持仓"), 
        std::string_view("A订单数"), std::string_view("B订单数"), 
        std::string_view("A撤单率"), std::string_view("B撤单率"), 
        std::string_view("A报单价成交率"), std::string_view("B报单价成交率"), 
        std::string_view("赚钱对数"), std::string_view("亏钱对数"),
        std::string_view("A腿卖一价"), std::string_view("A腿买一价"),
        std::string_view("B腿卖一价"), std::string_view("B腿买一价"),
        std::string_view("卖价差"), std::string_view("买价差"));

        using namespace trader;
        Asset asset = SS::env::trader->query_asset().value();       //一分钟查询延迟
        auto margin = (margin1 < margin2) ? margin1 : margin2;
        maxPosition = (int) ((asset.available * strategyCapiRatio) / margin);  //初始最大持仓值
        std::cout << __LINE__ << " " << maxPosition << std::endl;
    }
 
    void setOrderData(uint64_t data) {
        orderData = data;
    }

    std::vector<TickerID> getTickers() const {

        return std::vector<TickerID>{ticker1, ticker2};
    }

/*    
    vector<vector<float>> LoadData(const char* strFilePath)
    {
        vector<vector<float>> vecData;
        ifstream inFile(strFilePath);
        string strLine;
        int nRowCount = 0;
        getline(inFile, strLine);
        while (1)
        {
            getline(inFile, strLine);
            int nPos = strLine.find(",");
            if (nPos < 0)
            {
                break;
            }
            nRowCount ++;
            vector<float> vecTmp;
            while (nPos > 0)
            {
                string strTmp = strLine.substr(0, nPos);
                float fTmp = atof(strTmp.c_str());
                vecTmp.push_back(fTmp);
                strLine.erase(0, nPos + 1);
                nPos = strLine.find(",");
            } 
            float fTmp = atof(strLine.c_str());
            vecTmp.push_back(fTmp);
            vecData.push_back(vecTmp);
        }
        int nColCount = 0;
        if (nRowCount > 0)
        {
            nColCount = vecData[0].size();
        }
        float fData[nRowCount][nColCount];
        for (int nRow = 0; nRow < nRowCount; nRow ++)
        {
            vector<float> vecTmp = vecData[nRow];
            vecTmp.resize(nColCount, 0);
            for (int nCol = 0; nCol < nColCount; nCol ++)
            {
                fData[nRow][nCol] = vecTmp[nCol];
            }
            if (nRow < 10)
            {
                cout << fData[nRow][0] << endl;
            }
        }
        cout << "Data Row Count" << nRowCount << "Column Count" << nColCount;
        for (int i = 0; i < 10; i++)
        {
            for (int j = 0; j < 15; j++)
            {
                cout << "a[" << i << "][" << j << "];";
                cout << vecData[i][j]<< endl;
            }
        }
        return vecData;
    } 
*/

    bool isBalancedAndFinished() const {
        // std::cout << __LINE__ << " " << status.isBalance() << " " << finishOffset1 << " " << orderIds1.size() <<  " " << finishOffset2 << " " << orderIds2.size() << std::endl;
        return status.isBalance() && finishOffset1 == orderIds1.size() && finishOffset2 == orderIds2.size();
    }

    double quantile(vector<double>&x, double q){
        assert(q >= 0.0 && q <= 1.0);
        double id = (x.size() -1)*q;
        double qs = x[floor(id)];
        double h = (id - floor(id));
        return (1.0 - h) * qs + h * x[ceil(id)];
    }

    int onTick(TickerID ticker, int64_t type, int64_t pos){     //收到tick行情后
        if (!(running && (*pRunningConfig)->running)) return 0;
        if (ticker == ticker1) {
            auto q1 = *(quote1->get<1>(pos));
            aPrice1 = q1.level[0].ask_price;
            bPrice1 = q1.level[0].bid_price;
            lPrice1 = q1.last_price;
            time1 = q1.time;           
            amount1 = q1.amount;
            volume1 = q1.volume;
        } else if (ticker == ticker2) {
            auto q2 = *(quote2->get<1>(pos));
            bPrice2 = q2.level[0].bid_price;
            aPrice2 = q2.level[0].ask_price;
            lPrice2 = q2.last_price;
            time2 = q2.time;
            amount2 = q2.amount;
            volume2 = q2.volume;
        } else {
            return 0;
        }

        if (std::abs(time1 - time2) < 50*1000*1000) {       //取同步的行情后
            if (ATickSerialAskP.size() < 20 && BTickSerialAskP.size() < 20){        //间隔20个tick，即10秒取样更新一次价差值
                ATickSerialAskP.push_back(aPrice1);
                BTickSerialAskP.push_back(aPrice2);
                ATickSerialBidP.push_back(bPrice1);
                BTickSerialBidP.push_back(bPrice2);
            }else{
                aSprAver = aSprAver * 0.98 + (ATickSerialAskP.back() - BTickSerialAskP.back()) * 0.02;
                bSprAver = bSprAver * 0.98 + (ATickSerialBidP.back() - BTickSerialBidP.back()) * 0.02;
                ATickSerialAskP.clear();
                BTickSerialAskP.clear();
                ATickSerialBidP.clear();
                BTickSerialBidP.clear();
            }
            sprAver = (int)((aSprAver + bSprAver) * 0.5 / tick_size1) * tick_size1; //int or double  平滑计算最新价差
            if (sprAverSerial.size() < 180){        //存储半小时内价差序列
                sprAverSerial.push_back(sprAver);
            }else{  //存储后更新一次开平仓触发价
                int upSprAver = (int)quantile(sprAverSerial, 0.15);
                int downSprAver = (int)quantile(sprAverSerial, 0.85);
                if (upSprAver >= sprAverSerial.back() + (*pRunningConfig)->upOpenShort){
                    upOpenShort = upSprAver - sprAverSerial.back();
                }
                if (downSprAver <= sprAverSerial.back() + (*pRunningConfig)->downOpenLong){
                    downOpenLong = sprAverSerial.back() - downSprAver;
                }
                sprAverSerial.clear();
            }
            // int maxSprAver = *max_element(sprAverSerial.begin(), sprAverSerial.end());       //确定upOpenShort等
            // int minSprAver = *min_element(sprAverSerial.begin(), sprAverSerial.end());
            auto lastSprAsk = aPrice1 - aPrice2;
            auto lastSprBid = bPrice1 - bPrice2;
            // std::cout << __LINE__ << "__价差均值__" << sprAver << "__卖价差__" << lastSprAsk << "__买价差__" << lastSprBid << std::endl;
                

            auto longPos1 = longPositionHis1 + longPositionToday1;
            auto shortPos1 = shortPositionHis1 + shortPositionToday1;
            auto longPos2 = longPositionHis2 + longPositionToday2;
            auto shortPos2 = shortPositionHis2 + shortPositionToday2;
            double ratio = 1;
            double openProfit1 = 0;
            double openProfit2 =0;
            int effPosition = 0;
            if (longPos1 > 0){      //统计出头寸数量
                assert(shortPos1 == 0 && longPos2 == 0);
                openProfit1 = aPrice1 * longPos1 * contractMulti1 - avgOpenAmount1;
                openProfit2 = avgOpenAmount2 - aPrice2 * shortPos2 * contractMulti2;
                ratio = (double)longPos1 / (double)shortPos2;
                effPosition = longPos1;
            }else{
                openProfit1 = avgOpenAmount1 - bPrice1 * shortPos1 * contractMulti1;
                openProfit2 = bPrice2 *longPos2 * contractMulti2 - avgOpenAmount2;
                ratio = (double)shortPos1 / (double)longPos2;
                effPosition = -shortPos1;
            }
            
            //openProfit fee is hard to compute, only for reference，计算浮动盈亏
            if (std::isnan(ratio)) {  //empty
                openProfit = Profit{0,0};
            } else if (std::isinf(ratio)) {  //A opened but B empty
                openProfit = Profit{openProfit1, avgOpenFee1};
            } else {   //A closeed but B not finish AND normal
                openProfit = Profit{openProfit1+ratio*openProfit2, avgOpenFee1+ratio*avgOpenFee2};
            }

            openProfitStopLoss = (*pRunningConfig)->stoplossTick * tick_size1 * contractMulti1; //单手止损的值
            if(openProfit.profit >= std::abs(effPosition)*openProfitStopLoss) {     //未止损时
                // std::cout << __LINE__ << " " << effPosition << std::endl;
                quantity = 1;
                if(effPosition == 0){           //无仓位时，触发开多或开空
                    closeSpr.push_back(sprAver);
                    if (lastSprAsk >= closeSpr.back() + (*pRunningConfig)->upOpenShort){        //假定sprAver不变，不使用sprAverSerial.back()
                        side = Action::OpenShort;
                        //A腿盘口价差较大时，更激进挂A腿
                        if (std::abs(aPrice1 - bPrice1) > 1){
                            price1 = bPrice1 + 2 * tick_size1;
                        }else{
                            price1 = aPrice1 + ((*pRunningConfig)->sendSellA)*tick_size1;
                        }
                        price2 = aPrice2;
                        std::cout << __LINE__ << "无仓位--开空信号" << std::endl;
                    }else if(lastSprBid <= closeSpr.back() + (*pRunningConfig)->downOpenLong){//lastSprAsk如果等于lastSprBid
                        // std::cout << __LINE__ << " " << closeSpr.back() << std::endl;
                        //A腿盘口价差较大时，更激进挂A腿
                        if (std::abs(aPrice1 - bPrice1) > 1){
                            price1 = aPrice1 - 2 * tick_size1;
                        }else{
                            price1 = bPrice1 - ((*pRunningConfig)->sendBuyA)*tick_size1;
                        }
                        price2 = bPrice2;
                        side = Action::OpenLong;
                        std::cout << __LINE__ << "无仓位--开多信号" << std::endl;
                    }else{
                        side = Action::Empty;
                        return 0;
                    }
                }else if(effPosition > 0){      //有多头套利头寸时，继续开多或平仓多头
                    if (lastSprBid >= closeSpr.back() + ((*pRunningConfig)->downOpenLong + 2)){     //平仓条件:头寸长时间没有平仓成交
                        //触发平多头信号
                        if (std::abs(aPrice1 - bPrice1) > 1){
                            price1 = bPrice1 + 2 * tick_size1;
                        }else{
                            price1 = aPrice1 + ((*pRunningConfig)->sendSellA)*tick_size1;
                        }
                        price2 = bPrice2;
                        side = Action::CloseLong;
                        std::cout << __LINE__ << "有仓位--平多信号" << std::endl;
                        std::cout << __LINE__ << " lastSprBid " << lastSprBid << " close.back() " << closeSpr.back() << std::endl;
                        if (effPosition == 0){
                            closeSpr.push_back(closeSpr.back() + ((*pRunningConfig)->downOpenLong + 2));
                        }
                   
                    }else if(lastSprBid <= closeSpr.back() + (*pRunningConfig)->downOpenLong && std::abs(effPosition) <= maxPosition){
                        //触发继续开仓信号
                        if (cancelRatio2 >= 0.8){                     //成交率高则保持参数不变
                            if (std::abs(aPrice1 - bPrice1) > 1){     //A腿盘口价差较大时，更激进挂A腿
                                price1 = aPrice1 - 2 * tick_size1;
                            }else{
                                price1 = bPrice1 - ((*pRunningConfig)->sendBuyA)*tick_size1;
                            }
                            price2 = bPrice2;
                        }else{                                        //成交率低则调整超价参数，更贴近报价
                            if (std::abs(aPrice1 - bPrice1) > 1){
                                price1 = aPrice1 - 2 * tick_size1;
                                // std::cout << __LINE__ << std::endl;
                            }else{
                                price1 = bPrice1 - 0 * ((*pRunningConfig)->sendBuyA)*tick_size1;
                                // std::cout << __LINE__ << std::endl;
                            }
                            price2 = bPrice2;
                        }
                        side = Action::OpenLong;
                        // std::cout << __LINE__ << "有仓位--继续开多" << " " << price1 << std::endl;
                    }
                }else if(effPosition < 0){      //有空头套利头寸时，继续开空或平仓空头
                    if (lastSprAsk <= closeSpr.back() + ((*pRunningConfig)->upOpenShort - 2)){
                        //触发平空头信号
                        if (std::abs(aPrice1 - bPrice1) > 1){
                            price1 = aPrice1 - 2 * tick_size1;
                        }else{
                            price1 = bPrice1 - ((*pRunningConfig)->sendBuyA)*tick_size1;
                        }
                        price2 = aPrice2;
                        side = Action::CloseShort;
                        // std::cout << __LINE__ << "有仓位--平空信号" << std::endl;
                        if (effPosition == 0){
                            closeSpr.push_back(closeSpr.back() + ((*pRunningConfig)->upOpenShort + 2));            //更新平仓时的价差做为下一次交易的中心值
                        }
                    
                    }else if (lastSprAsk >= closeSpr.back() + (*pRunningConfig)->upOpenShort && std::abs(effPosition) <= maxPosition){
                        //触发继续开空仓信号
                        if (cancelRatio2 >= 0.8){                   //成交率高则保持参数不变
                            if (std::abs(aPrice1 - bPrice1) > 1){   //A腿盘口价差较大时，更激进挂A腿
                                price1 = bPrice1 + 2 * tick_size1;
                            }else{
                                price1 = aPrice1 + ((*pRunningConfig)->sendSellA)*tick_size1;
                            }
                            price2 = aPrice2;
                        }else{                                      //成交率低则调整超价参数，AB腿更贴近报价
                            if (std::abs(aPrice1 - bPrice1) > 1){   
                                price1 = bPrice1 + 2 * tick_size1;
                            }else{
                                price1 = aPrice1 + 0 * ((*pRunningConfig)->sendSellA)*tick_size1;
                            }
                            price2 = aPrice2;
                        }
                        side = Action::OpenShort;
                        // std::cout << __LINE__ << "有仓位--继续开空" << std::endl;
                    }
                }                
            } else {        //止损时
                if (effPosition > 0) {
                    side = Action::CloseLong;
                    price1 = aPrice1 - 3 * tick_size1;//wrong
                    price2 = aPrice2;
                } else {
                    side = Action::CloseShort;
                    price1 = bPrice1 + 3 * tick_size1;
                    price2 = bPrice2;
                }
            }  
            
            bool cancelFlag = false;        //A腿止损小，B腿止损大，A=2，B=3/4
            for (auto i=finishOffset1; i < orderIds1.size(); ++i) {
                const trader::Order* o = SS::env::trader->query_order_static(orderIds1[i]);
                switch(side) {
                    case Action::OpenLong:
                    case Action::CloseShort:
                        if (o->side == trader::SideType::BUY && o->price >= bPrice1 - ((*pRunningConfig)->cancelBuyA)*tick_size1) break; //cancelBuyA >= 0
                        else goto CANCEL;
                    case Action::OpenShort:
                    case Action::CloseLong:
                        if (o->side == trader::SideType::SELL && o->price <= aPrice1 + ((*pRunningConfig)->cancelSellA)*tick_size1) break; //cancelSellA >= 0
                        else goto CANCEL;
                CANCEL:
                    default:
                        if (cancelCount1 < cancelLimit1) {
                            trader::CancelOrder co;
                            co.order_id = orderIds1[i];
                            SS::env::trader->cancel_order(co);
                            cancelFlag = true;
                        }
                }
            }

            ++startPairCouter;
            if(isBalancedAndFinished()) {       //AB数量匹配，套利仓位正确后
                if ((side == Action::OpenLong || side == Action::OpenShort) && std::abs(effPosition) < maxPosition){      //开仓，且未到达指定仓位时
                    std::cout << __LINE__ << " effPostion " << effPosition << " maxPosition " << maxPosition << std::endl;
                    startPair(startPairCouter);
                }else if ((side == Action::CloseLong || side == Action::CloseShort) && (std::abs(effPosition) <= maxPosition)){       //平仓，且未到达指定仓位时
                    std::cout << __LINE__ << " effPostion " << effPosition << " maxPosition " << maxPosition << std::endl;
                    startPair(startPairCouter);
                }else{      //仓位已经到达后
                    std::cout << __LINE__ << " 停止报A" << std::endl;
                }
            }
            
            
            SS::env::LOG(*logFile, std::string_view("{:tm},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{}\n"), 
            std::chrono::duration_cast<std::chrono::milliseconds>(mio::chrono::now()),
            closeProfit.netProfit(), openProfit.profit, closeProfit.fee, 
            longPos1-shortPos1, longPos2-shortPos2, 
            orderIds1.size(), orderIds2.size(), 
            cancelRatio1, cancelRatio2, 
            onPriceRatio1, onPriceRatio2, 
            gainPairCount, lossPairCount,
            aPrice1,bPrice1,
            aPrice2,bPrice2,
            lastSprAsk, lastSprBid);
        }
        return 0;
    }

    template<bool isLeg1>
    int64_t insertOrder(trader::Order& ord) {
        int64_t oid = SS::env::trader->insert_order(ord);
        if (oid <= 0) {
            exit(oid);
        }
        if constexpr (isLeg1) {
            orderIds1.push_back(oid);
            finishFlags1.push_back(false);
            closeProfits1.push_back(Profit());
            pairProfits.push_back(Profit());
            offsets.push_back(orderIds2.size());
        } else {
            orderIds2.push_back(oid);
            finishFlags2.push_back(false);
            closeProfits2.push_back(Profit());
        }
        return oid;
    }

    int startPair(uint32_t spc) {       //报出A腿
        if (spc < startPairCouter){
            return 0;
        }
        using namespace trader;
        Order o;
        o.data = orderData + orderIds1.size();
        o.ticker = ticker1;
        // if (time1 > 23:00 ){ //time compare
        //     o.price_type = PriceType::LIMIT; 
        // }else{
        //     o.price_type = PriceType::FAK; 
        // }
        //判断报A腿方向、数量       
        o.price_type = PriceType::LIMIT;
        o.time = mio::chrono::now();
        switch(side) {
            case Action::Empty: 
                return 0;
            case Action::OpenLong:
                o.side = SideType::BUY;
                o.price = price1;
                o.quantity = quantity;
                o.offset = OffsetType::OPEN;
                break;
            case Action::OpenShort:
                o.side = SideType::SELL;
                o.price = price1;
                o.quantity = quantity;
                o.offset = OffsetType::OPEN;
                break;
            case Action::CloseLong:
                o.side = SideType::SELL;
                o.price = price1;
                if (longPositionHis1 > 0) {
                    o.offset = OffsetType::CLOSE_YESTERDAY;
                    o.quantity = quantity > longPositionHis1 ? longPositionHis1 : quantity;
                } else {
                    o.offset = OffsetType::CLOSE_TODAY;
                    o.quantity = quantity > longPositionToday1 ? longPositionToday1 : quantity;
                }
                break;      
            case Action::CloseShort:
                o.side = SideType::BUY;
                o.price = price1;
                if (shortPositionHis1 > 0) {
                    o.offset = OffsetType::CLOSE_YESTERDAY;
                    o.quantity = quantity > shortPositionHis1 ? shortPositionHis1 : quantity;
                } else {
                    o.offset = OffsetType::CLOSE_TODAY;
                    o.quantity = quantity > shortPositionToday1 ? shortPositionToday1 : quantity;
                }
                break;
        }
        
        if (o.quantity > 0) {
            std::cout << __LINE__<< o.ticker.to_string() << " " << o.quantity << " 报出价 " << o.price  << " " << trader::to_string(o.side) <<  " " << trader::to_string(o.offset) << " " << trader::to_string(o.price_type) <<  "卖一价" << aPrice1 << "买一价" << bPrice1 <<  " sprask " << (aPrice1-aPrice2) << " sprbid " << (bPrice1 - bPrice2) << std::endl;
            //cu2206.SHFE 1 7355 SELL OPEN LIMIT
            insertOrder<true>(o);
        }
        return 0;
    }

    template<bool isLeg1, bool isBuy>
    int computeProfit(const trader::OrderRes& res, uint64_t idIndex) {
        using namespace trader;
        OrderStatus *os;
        int64_t *openOffsetQuantity;
        std::vector<int32_t> *orderIds;
        uint64_t *openOffset;
        std::vector<Profit> *closeProfits;
        double *avgOpenAmount;
        double *avgOpenFee;
        int contractMulti;
        if constexpr (isLeg1) {
            os = &OrderStatus1;
            openOffsetQuantity = &openOffsetQuantity1;
            orderIds = &orderIds1;
            openOffset = &openOffset1;
            closeProfits = &closeProfits1;
            avgOpenAmount = &avgOpenAmount1;
            avgOpenFee = &avgOpenFee1;
            contractMulti = contractMulti1;
        } else {
            os = &OrderStatus2;
            openOffsetQuantity = &openOffsetQuantity2;
            orderIds = &orderIds2;
            openOffset = &openOffset2;
            closeProfits = &closeProfits2;
            avgOpenAmount = &avgOpenAmount2;
            avgOpenFee = &avgOpenFee2;
            contractMulti = contractMulti2;
        }

        auto q = res.quantity;
        double matchAmount = 0;
        double matchFee = 0;
        while((q -= (os->quantity_traded - *openOffsetQuantity)) > 0) {
            double ratio = os->quantity_traded > 0 ? (1.0 - (double)(*openOffsetQuantity)/(double)(os->quantity_traded)) : 0.0;
            matchAmount += ratio * os->total_amount;
            matchFee += ratio * os->handling_fee;

            *openOffsetQuantity = 0;
            while(SS::env::trader->query_order_static((*orderIds)[++(*openOffset)])->offset != OffsetType::OPEN);
            *os = SS::env::trader->query_order_status((*orderIds)[*openOffset]).value();
        }

        auto traded = q + os->quantity_traded - *openOffsetQuantity;
        *openOffsetQuantity += traded;
        double ratio = (double)traded /(double)(os->quantity_traded);
        matchAmount += ratio * os->total_amount;
        matchFee += ratio * os->handling_fee;

        *avgOpenAmount -= matchAmount;
        *avgOpenFee -= matchFee;

        Profit p;
        p.fee = matchFee + res.handling_fee; 
        if constexpr (isBuy) {
            p.profit = matchAmount - res.price*res.quantity * contractMulti;
        } else {
            p.profit = res.price*res.quantity * contractMulti - matchAmount;
        }
        (*closeProfits)[idIndex] += p;
        closeProfit += p;
        return 0;
    }

    Action getAction(const trader::Order& ord) const {      //根据A订单开平和方向确定套利方向
        if (ord.side == trader::SideType::BUY) {
            return ord.offset == trader::OffsetType::OPEN ? Action::OpenLong : Action::CloseShort;
        } else {
            return ord.offset == trader::OffsetType::OPEN ? Action::OpenShort : Action::CloseLong;
        }
    }

    int onOrder(const trader::OrderRes& res, const trader::Order& ord) {        //收到订单回报后
        if (!(running && (*pRunningConfig)->running)) return 0;
        using namespace trader;
        if (ord.ticker == ticker1) {    //处理A
            if (res.quantity > 0) {     //A腿订单接收到回报后
                Order o;
                o.data = orderData + orderIds2.size();
                o.ticker = ticker2;
                o.price_type = PriceType::FAK;
                o.offset = ord.offset;
                o.quantity = res.quantity;
                o.time = mio::chrono::now();
                reInsertOrderB = 0;
                ATime.push_back(o.time);        //A腿报出的时间
                std::cout << __LINE__ << " ATime.size " << ATime.size() << " ATime.back " << mio::to_string(ATime.back()) << std::endl;
                // std::chrono::microseconds a = ATime/1000;
                // a.count();
                if (res.side == SideType::BUY) {
                    o.price = price2;
                    o.side = SideType::SELL;
                    insertOrder<false>(o);
                    std::cout << __LINE__ << mio::to_string(o.time) << o.ticker.to_string() << " " << o.quantity << " 报出价 " << o.price  << " " << trader::to_string(o.side) <<  " " << trader::to_string(o.offset) << " " << trader::to_string(o.price_type) << "卖一价" << aPrice2 << "买一价" << bPrice2 <<  " sprask " << (aPrice1-aPrice2) << " sprbid " << (bPrice1 - bPrice2) << std::endl;
                    switch(res.offset) {
                        case OffsetType::CLOSE_YESTERDAY: {
                            shortPositionHis1 -= res.quantity;
                            status = PosStatus::ShortPartialLong;
                            computeProfit<true, true>(res, ord.data-orderData);
                            break;
                        }
                        case OffsetType::CLOSE_TODAY: {
                            shortPositionToday1 -= res.quantity;
                            status = PosStatus::ShortPartialLong;
                            computeProfit<true, true>(res, ord.data-orderData);
                            break;
                        }
                        case OffsetType::OPEN: {
                            longPositionToday1 += res.quantity;
                            status = PosStatus::LongPartialLong;
                            avgOpenAmount1 += res.price*res.quantity*contractMulti1;
                            avgOpenFee1 += res.handling_fee;
                        }
                    }
                } else if (res.side == SideType::SELL) {
                    o.price = price2;
                    o.side = SideType::BUY;
                    insertOrder<false>(o);
                    std::cout << __LINE__ << " time " << mio::to_string(mio::chrono::now()) << " 合约 " << o.ticker.to_string() << " " << o.quantity << " 报出价 " << o.price  << " " << trader::to_string(o.side) <<  " " << trader::to_string(o.offset) << " " << trader::to_string(o.price_type) << "卖一价" << aPrice2 << "买一价" << bPrice2 << " 卖价差 " << (aPrice1-aPrice2) << " 买价差 " << (bPrice1 - bPrice2) << std::endl;
                    switch(res.offset) {
                        case OffsetType::CLOSE_YESTERDAY: {
                            longPositionHis1 -= res.quantity;
                            status = PosStatus::LongPartialShort;
                            computeProfit<true, false>(res, ord.data-orderData);
                            break;
                        }
                        case OffsetType::CLOSE_TODAY: {
                            longPositionToday1 -= res.quantity;
                            status = PosStatus::LongPartialShort;
                            computeProfit<true, false>(res, ord.data-orderData);
                            break;
                        }
                        case OffsetType::OPEN: {
                            shortPositionToday1 += res.quantity;
                            status = PosStatus::ShortPartialShort;
                            avgOpenAmount1 += res.price*res.quantity*contractMulti1;
                            avgOpenFee1 += res.handling_fee;
                        }
                    }
                }
            }
            
            if (res.is_finally()) {     //A腿回报状态不再改变时
                auto idIndex = ord.data - orderData;
                finishFlags1[idIndex] = true;
                while(finishOffset1 < finishFlags1.size() && finishFlags1[finishOffset1]) {
                    finishOffset1++;
                }
                OrderStatus osts1 = SS::env::trader->query_order_status(res.order_id).value();
                int64_t q = ord.quantity - osts1.quantity_traded;
                
                if (q > 0) {        //计算A腿撤单率
                    ++cancelCount1;
                } else {
                    ++allTradedCount1;
                }
                cancelRatio1 = (double)cancelCount1 / (cancelCount1+allTradedCount1);

                // if(isBalancedAndFinished()) {        //继续报出A腿
                //     std::cout << __LINE__ << std::endl;
                //     if (res.offset != OffsetType::OPEN) {
                //         std::cout << __LINE__ << std::endl;
                //         pairProfits.back() = closeProfits1.back();
                //         for (auto i = offsets.back(); i < orderIds2.size(); ++i) {
                //             pairProfits.back() += closeProfits2[i];
                //         }
                //         if(pairProfits.back().netProfit() > 0){
                //             ++gainPairCount;
                //             if (q > 0) {
                //                 startPair(startPairCouter);
                //             } else {
                //                 quantity *= 2;
                //                 if (quantity > 4) quantity = 1;
                //                 //平仓盈利则继续开空或继续开多
                //                 if (res.side == SideType::BUY){
                //                     std::cout << __LINE__ << std::endl;
                //                     side = Action::CloseShort;
                //                     //捕捉A腿有利价差
                //                     if (std::abs(aPrice1 - bPrice1) > 1){
                //                         price1 = bPrice1 + tick_size1;
                //                     }else{
                //                         price1 = aPrice1 + ((*pRunningConfig)->sendSellA)*tick_size1;
                //                     }
                //                     price2 = aPrice2 - tick_size2;
                //                 } else {
                //                     std::cout << __LINE__ << std::endl;
                //                     side = Action::CloseShort;
                //                     //捕捉A腿有利价差
                //                     if (std::abs(aPrice1 - bPrice1) > 1){
                //                         price1 = aPrice1 - tick_size1;
                //                     }else{
                //                         price1 = bPrice1 - ((*pRunningConfig)->sendBuyA)*tick_size1; //
                //                     }
                //                     price2 = bPrice2 + tick_size2;
                //                 }
                //                 using namespace std::chrono_literals;
                //                 drive->use_event<SS::TimerEvent>()->add_for(20ms, [this, spc=this->startPairCouter]() {
                //                     return this->startPair(spc);
                //                 });
                //             }
                //         }else {
                //             if(osts1.quantity_traded > 0) ++lossPairCount;
                //             if (q > 0) {
                //                 startPair(startPairCouter);
                //             } else {
                //                 quantity = 1;
                //                 if (res.side == SideType::BUY) {
                //                     std::cout << __LINE__ << std::endl;
                //                     side = Action::CloseShort;
                //                     //捕捉A腿有利价差
                //                     if (std::abs(aPrice1 - bPrice1) > 1){
                //                         price1 = aPrice1 - tick_size1;
                //                     }else{
                //                         price1 = bPrice1 - ((*pRunningConfig)->sendBuyA)*tick_size1; //
                //                     }
                //                     price2 = bPrice2 + tick_size2;
                //                 } else {
                //                     std::cout << __LINE__ << std::endl;
                //                     side = Action::CloseLong;
                //                     //捕捉A腿有利价差
                //                     if (std::abs(aPrice1 - bPrice1) > 1){
                //                         price1 = bPrice1 + tick_size1;
                //                     }else{
                //                         price1 = aPrice1 + ((*pRunningConfig)->sendSellA)*tick_size1;
                //                     }
                //                     price2 = aPrice2 - tick_size2;
                //                 }
                //             }
                //         }
                //     } else {
                //         if (q == 0) {
                //             if (res.side == SideType::BUY) {
                //                 std::cout << __LINE__ << std::endl;
                //                 side = Action::OpenLong;
                //                 //平多头套利
                //                 price1 = bPrice1 - tick_size1;
                //                 price2 = bPrice2;
                //             } else {
                //                 side = Action::OpenShort;
                //                 price1 = aPrice1 + tick_size1;
                //                 price2 = aPrice2;
                //             }
                //         }   
                //         ++loopNum;
                //         if (loopNum <= loopCount){
                //             std::cout << __LINE__ << " " << loopNum << std::endl;
                //             startPair(startPairCouter);
                //         }else{
                //             std::cout << __LINE__ << " A开仓循环到达次数，暂停" << std::endl;
                //         }   
                //     }
                // }
                
                if (osts1.quantity_traded > 0){     //计算A腿成交率
                    double average = osts1.total_amount/(osts1.quantity_traded*contractMulti1);
                    if (ord.price == average){
                        ++onPriceCount1;
                    }else{
                        ++betterPriceCount1;
                    }
                    onPriceRatio1 = (double)onPriceCount1 / (onPriceCount1 + betterPriceCount1);
                }
            }
        }
        else if (ord.ticker == ticker2) {       //处理B
            if (res.quantity > 0) {     //B腿订单接收到回报后
                if (res.side == SideType::SELL) {       //修改仓位数量，计算盈亏
                    switch(res.offset) {
                        case OffsetType::CLOSE_YESTERDAY: {
                            longPositionHis2 -= res.quantity;
                            auto longPos = longPositionHis2 + longPositionToday2;
                            if ( longPos == (shortPositionHis1 + shortPositionToday1)) {
                                status = longPos > 0 ? PosStatus::Short : PosStatus::Empty; 
                            }
                            computeProfit<false, false>(res, ord.data-orderData);
                            break;
                        }
                        case OffsetType::CLOSE_TODAY:{
                            longPositionToday2 -= res.quantity;
                            auto longPos = longPositionHis2 + longPositionToday2;                        
                            if ( longPos == (shortPositionHis1 + shortPositionToday1)) {
                                status = longPos > 0 ? PosStatus::Short : PosStatus::Empty; 
                            }
                            computeProfit<false, false>(res, ord.data-orderData);
                            break;
                        }
                        case OffsetType::OPEN: {
                            shortPositionToday2 += res.quantity;
                            auto shortPos = shortPositionHis2 + shortPositionToday2;
                            if (shortPos == (longPositionHis1 + longPositionToday1)) {
                                status = PosStatus::Long;
                            }
                            avgOpenAmount2 += res.price*res.quantity*contractMulti2;
                            avgOpenFee2 += res.handling_fee;
                        }
                    }
                } else if (res.side == SideType::BUY) {
                    switch(res.offset) {
                        case OffsetType::CLOSE_YESTERDAY: {
                            shortPositionHis2 -= res.quantity;
                            auto shortPos = shortPositionHis2 + shortPositionToday2;
                            if (shortPos == (longPositionHis1 + longPositionToday1)) {
                                status = shortPos > 0 ? PosStatus::Long : PosStatus::Empty;
                            }
                            computeProfit<false, true>(res, ord.data-orderData);
                            break;
                        }
                        case OffsetType::CLOSE_TODAY: {
                            shortPositionToday2 -= res.quantity;
                            auto shortPos = shortPositionHis2 + shortPositionToday2;
                            if (shortPos == (longPositionHis1 + longPositionToday1)) {
                                status = shortPos > 0 ? PosStatus::Long : PosStatus::Empty;
                            }
                            computeProfit<false, true>(res, ord.data-orderData);
                            break;
                        }
                        case OffsetType::OPEN: {
                            longPositionToday2 += res.quantity;
                            auto longPos = longPositionHis2 + longPositionToday2;
                            if (longPos == (shortPositionHis1 + shortPositionToday1)) {
                                status = PosStatus::Short;
                            }
                            avgOpenAmount2 += res.price*res.quantity*contractMulti2;
                            avgOpenFee2 += res.handling_fee;
                        }
                    }
                }
            }

            if (res.is_finally()){     //B腿回报状态不再改变时
                auto idIndex = ord.data - orderData;
                finishFlags2[idIndex] = true;
                while(finishOffset2 < finishFlags2.size() && finishFlags2[finishOffset2]) {
                    finishOffset2++;
                } 
                OrderStatus osts = SS::env::trader->query_order_status(res.order_id).value();
                auto q = ord.quantity - osts.quantity_traded;
                if (q > 0){     //B腿未成交或部分成交时，继续报出B腿
                    Order o(ord);
                    o.data = orderData + orderIds2.size();
                    o.quantity = q;
                    // if (reInsertOrderB < (std::abs((*pRunningConfig)->stoplossTick)-2)){
                    //     o.price_type = PriceType::LIMIT;
                    //     o.price += o.side == SideType::BUY ? tick_size2 : -tick_size2;
                    //     reInsertOrderB ++;
                    // }else{
                    //     o.price_type = PriceType::FAK;
                    //     o.price += o.side == SideType::BUY ? 2*tick_size2 : -2*tick_size2;
                    // }
                    o.price_type = PriceType::FAK;
                    o.price += o.side == SideType::BUY ? tick_size2 : -tick_size2;
                    o.time = mio::chrono::now();
                    insertOrder<false>(o);
                    std::cout << __LINE__ << mio::to_string(o.time) << o.ticker.to_string() << " " << o.quantity << " 报出价 " << o.price  << " " << trader::to_string(o.side) <<  " " << trader::to_string(o.offset) << " " << trader::to_string(o.price_type) << "卖一价" << aPrice2 << "买一价" << bPrice2 << " sprask " << (aPrice1-aPrice2) << " sprbid " << (bPrice1 - bPrice2) << std::endl;
                    
                    // if (ord.price_type == PriceType::FAK){
                    //     ++cancelCountFak2;
                    // }else if (ord.price_type == PriceType::LIMIT){
                    //     ++cancelCountLimit2;
                    // }
                    ++cancelCountFak2;
                } else {        //B腿全部成交后，等待报出A腿
                    ++allTradedCount2;
                    if (isBalancedAndFinished()) {      //套利数量平衡时
                        if (res.offset != OffsetType::OPEN) {       //如果B腿是平仓，计算套利平仓盈亏
                            pairProfits.back() = closeProfits1.back();
                            for (auto i = offsets.back(); i < orderIds2.size(); ++i) {
                                pairProfits.back() += closeProfits2[i];
                            }

                            if(pairProfits.back().netProfit() > 0){             //平仓盈利时,增加平仓数量
                                ++gainPairCount;
                                // strategyCapiRatio *= 2;
                                if (res.side == SideType::BUY){     //调整A腿B腿报出价格
                                    side = Action::CloseShort;
                                    if (std::abs(aPrice1 - bPrice1) > 1){
                                        price1 = aPrice1 - 2 * tick_size1;
                                    }else{
                                        price1 = bPrice1 - ((*pRunningConfig)->sendBuyA)*tick_size1; //
                                    }
                                    price2 = aPrice2;
                                } else {
                                    side = Action::CloseLong;
                                    if (std::abs(aPrice1 - bPrice1) > 1){
                                        price1 = bPrice1 + 2 * tick_size1;
                                    }else{
                                        price1 = aPrice1 + ((*pRunningConfig)->sendSellA)*tick_size1;
                                    }
                                    price2 = bPrice2;
                                }

                                BTime.push_back(ord.time);      //B腿收到成交回报，完全补上A后的时间 ??ord未初始化
                                std::cout << __LINE__ << " BTime.size " << BTime.size() << " BTime.back " << mio::to_string(BTime.back()) << std::endl;
                                auto duration = ((BTime.back() - ATime.front())/1000).count();
                                std::cout << __LINE__ << " duration " << duration << std::endl;
                                if (duration <= 450){   
                                    sumQuantity += ord.quantity;
                                    if (sumQuantity < maxPosition){
                                        if (quantity <= maxLot){
                                            quantity *= 2;
                                            std::cout << __LINE__ << " 前半部分报单 " << std::endl;
                                            startPair(startPairCouter);
                                        }else{
                                            quantity = 1;
                                            ++loopNum;
                                            if (loopNum <= loopCount){
                                                std::cout << __LINE__ << " 后半部分报单 " << std::endl;
                                                using namespace std::chrono_literals;
                                                drive->use_event<SS::TimerEvent>()->add_for(20ms, [this, spc=this->startPairCouter]() {
                                                    return this->startPair(spc);
                                                });
                                            }else{
                                                std::cout << " 循环次数已到 " << std::endl;
                                            }
                                        }
                                    }else{
                                        std::cout << " 数量足够 " << std::endl;
                                    }
                                }else{
                                    quantity = 1;
                                    std::cout << __LINE__ << std::endl;
                                }
                            }else {                                             //亏损平仓时,减少平仓数量,等待下一次tick
                                ++lossPairCount;
                                // strategyCapiRatio *= 0.5;
                                quantity = 1;

                                if (res.side == SideType::BUY) {        //调整A腿B腿价格
                                    side = Action::CloseLong;
                                    price1 = aPrice1 + ((*pRunningConfig)->sendSellA)*tick_size1;
                                    price2 = bPrice2;
                                } else {
                                    side = Action::CloseShort;
                                    price1 = bPrice1 - ((*pRunningConfig)->sendBuyA)*tick_size1;
                                    price2 = aPrice2;
                                }
                            }
                        } else{     //如果B腿是开仓
                            if (res.side == SideType::BUY) {        //修改价格
                                side = Action::OpenShort;
                                if (std::abs(aPrice1 - bPrice1) > 1){   //A腿盘口价差较大时，更激进挂A腿
                                    price1 = bPrice1 + 2 * tick_size1;
                                }else{
                                    price1 = aPrice1 + ((*pRunningConfig)->sendSellA)*tick_size1;
                                }
                                price2 = aPrice2;
                            } else {
                                side = Action::OpenLong;
                                if (std::abs(aPrice1 - bPrice1) > 1){     //A腿盘口价差较大时，更激进挂A腿
                                    price1 = aPrice1 - 2 * tick_size1;
                                }else{
                                    price1 = bPrice1 - ((*pRunningConfig)->sendBuyA)*tick_size1;
                                }
                                price2 = aPrice2;
                            }

                            BTime.push_back(ord.time);      //B腿收到成交回报，完全补上A后的时间
                            std::cout << __LINE__ << " BTime.size " << BTime.size() << " BTime.back " << mio::to_string(BTime.back()) << std::endl;
                            auto duration = ((BTime.back() - ATime.front())/1000).count();
                            std::cout << __LINE__ << " duration " << duration << std::endl;
                            if (duration <= 450){   
                                sumQuantity += ord.quantity;
                                if (sumQuantity < maxPosition){
                                    if (quantity <= maxLot){
                                        quantity *= 2;
                                        std::cout << __LINE__ << " 前半部分报单 " << std::endl;
                                        startPair(startPairCouter);
                                    }else{
                                        quantity = 1;
                                        ++loopNum;
                                        if (loopNum <= loopCount){
                                            std::cout << __LINE__ << " 后半部分报单 " << std::endl;
                                            using namespace std::chrono_literals;
                                            drive->use_event<SS::TimerEvent>()->add_for(20ms, [this, spc=this->startPairCouter]() {
                                                return this->startPair(spc);
                                            });
                                        }else{
                                            std::cout << " 循环次数已到 " << std::endl;
                                        }
                                    }
                                }else{
                                    std::cout << " 数量足够 " << std::endl;
                                }
                            }else{
                                quantity = 1;
                                std::cout << __LINE__ << std::endl;
                                if (cancelCount1 < cancelLimit1) {
                                    trader::CancelOrder co;
                                    co.order_id = orderIds1[ord.order_id];
                                    SS::env::trader->cancel_order(co);
                                }
                            }
                        }
                    }
                }
                // std::cout << __LINE__ << " maxPosition " << maxPosition << std::endl;
                cancelRatio2 = (double)cancelCountLimit2 / (cancelCountLimit2 + allTradedCount2);       //计算B腿撤单率
                
                if (osts.quantity_traded > 0){      //计算B腿成交率
                    double average = osts.total_amount/(osts.quantity_traded*contractMulti2);//average声明

                    if (ord.price == average){
                        ++onPriceCount2;
                    }
                    else{
                        ++betterPriceCount2;
                    }
                    onPriceRatio2 = (double)onPriceCount2 / (onPriceCount2 + betterPriceCount2);
                }
 
/*                     if (res.offset != OffsetType::OPEN) {
                        //统计pairProfits趋势ice  << " " << trader::to_string(o.side) <<  " " << trader::to_string(o.offset) << " " << trader::to_string(o.price_type) << "__aPrice__
                            sum2 -= nearPairProfits[j - (lenOfFront - 1)];
                        }
                        //调整策略总资金分配比例
                        strategyCapiRatio *= (maPairProfits.at(maPairProfits.size() -2) > maPairProfits.back()) ? 2 : 0.5;                               
                        Asset asset1 = SS::env::trader->query_asset();
                        margin = (margin1 < margin2) ? margin1 : margin2;
                        maxPosition = (int) ((asset1.available * strategyCapiRatio) / margin);
                    }

                    SS::env::LOG(std::cout, std::string_view("{} {}"), std::string_view("策略占用资金比例为:\n"), strategyCapiRatio);
                    SS::env::LOG(std::cout, std::string_view("{} {}"), std::string_view("策略最大仓位为:\n"), maxPosition); */

                    //strategy capital use
/*                     if (pairProfits.back().netProfit() > 0){   
                        if (sumLot < maxPosition){ 
                            if (loopCount <= 2){   
                                posStep2 = 1; 
                            }else if (loopCount > 2 && loopCount < 4){  
                                posStep2 = 0;  
                            }else{
                                posStep2 = posStep2 + 1; 
                            }
                        }
                        posStep[loopCount] =  posStep[loopCount-1] + posStep2; 
                        lot[loopCount] = lot[loopCount-1] + posStep[loopCount]; 
                        sumLot += lot[loopCount];  

                        if (ord.side == SideType::BUY){//A是卖单
                            overPri1 = (LTickAver > (aPrice1 - bPrice1) / 2) ? 1 : 2;   //加速A腿成交               
                        }
                        else if(ord.side == SideType::SELL){
                            overPri1 = (LTickAver < (aPrice1 - bPrice1) / 2) ? 1 : 2;               
                        }
                    }else if (pairProfits.back().netProfit() < 0){  
                        if (sumLot < maxPosition){ 
                            if (loopCount <= 3){  
                                lotClose = 2 * inilot;
                            }else{
                                lotClose = 20 - sumLot;
                            }
                            sumLot += lotClose; 
                        }
                        std::cout << lotClose << std::endl; 
                        //调整A超价数量
                        if (ord.side == SideType::BUY){
                            overPri1 = (LTickAver > (aPrice1 - bPrice1) / 2) ? 1 : 2;
                        }
                        else if(ord.side == SideType::SELL){
                            overPri1 = (LTickAver > (aPrice1 - bPrice1) / 2) ? 1 : 2;               
                        }
                    }else{
                        SS::env::LOG(std::cout, std::string_view("平仓无收益\n"));
                    } 
                    loopCount += 1; */ //循环次数
 
                    /*
                    //统计tick内均价变化
                    double mount1[10], turnover[10], tickAvr[10];
                    double sumA;
                    for (int i = 0; i < 10; i ++){
                        tickAvr[i] = turnover[i] / mount1[i];
                        sumA += tickAvr[i];
                    }
                    tickAver = sumA / 10;  //计算tick内成交价格变化
                    */                                                    
            }
        } 
        else {      //错误退出
            exit(ord.order_id); //error!
        }
        return 0;
    }
    
    int onCancel(const trader::CancelRes& res, const trader::Order& ord){        
        return 0;
    }

    ~PairTrader() = default;
};

//订单处理路由
template<class> inline static constexpr bool always_false_v = false;
class OrderInfoRouter {
    private:
        std::vector<std::shared_ptr<PairTrader>> traders;
        const uint32_t lShift;
    public:
        OrderInfoRouter(uint32_t lsft = 56):lShift(lsft){}

        void routeRegister(const std::shared_ptr<PairTrader>& trader){
            traders.push_back(trader);
            trader->setOrderData(uint64_t(traders.size()-1) << lShift);
        }
        int onOrder(const std::variant<trader::OrderRes, trader::CancelRes> &res) {
            using namespace trader;
            std::visit([this](auto&& arg) {
                using T = std::decay_t<decltype(arg)>;
                if constexpr (std::is_same_v<T, OrderRes>) {
                    const Order* ord = SS::env::trader->query_order_static(arg.order_id);
                    this->traders[ord->data >> lShift]->onOrder(arg, *ord);
                } else if constexpr (std::is_same_v<T, CancelRes>) {
                    const Order* ord = SS::env::trader->query_order_static(arg.order_id);
                    this->traders[ord->data >> lShift]->onCancel(arg, *ord);
                } else static_assert(always_false_v<T>, "non-exhaustive visitor!");
            }, res);
            return 0;
        }
};

std::unique_ptr<OrderInfoRouter> oir;
//trader []xunhuan duqu shuchu cangwei poshis1, poshis2
std::vector<std::shared_ptr<SS::SignalManager>> sms;
void a(){
    // std::cout << __LINE__ << "__1360__" << "函数入口地方" << std::endl;
    // Json::Value root;
    
    // ofstream os;
    // os.open("/home/DuShuai/simnow/configs/ag2212_ag2206.json", std::ios::out | std::ios::app);
    // if (!os.is_open()){ 
    // }
    vector<int> a = { 2,4,6,7,1,0,8,9,6,3,2 };
    auto maxPosition = max_element(a.begin(), a.end());
    cout << *maxPosition << " at the postion of " << maxPosition - a.begin() <<endl;
    //cout << a[maxPosition - a.begin()] << " at the postion of " << distance(a.begin(), maxPosition) << endl;
    system("pause");
}

extern "C"
{
    int strategy_start(int argc, char **argv)
    {
        // a();

        using namespace std::placeholders;
        using namespace std::chrono_literals;
        drive = SS::env::drive<drive_t>;
        auto quote = drive->use_event<SS::QuoteEvent>();
        oir = std::make_unique<OrderInfoRouter>();
        // std::vector<std::shared_ptr<PairTrader>> traders;
        const std::filesystem::path configs{"configs"};
        //ag2207_ag2206.json set 0/delete  hisOrderStatus1,hisOrderStatus2
        for (auto const& file : std::filesystem::directory_iterator{configs}) {
            if (file.is_regular_file()) {
                auto p = file.path();
                if (p.filename().string().find("running") != std::string::npos) continue;
                auto sm = std::make_shared<SS::SignalManager>();
                auto trader = std::make_shared<PairTrader>(file.path());
                sm->add_signal(p.filename().string(), [trader](TickerID ticker, int64_t type, int64_t pos){
                    return trader->onTick(ticker,type,pos);
                });
                for (auto& t : trader->getTickers()){
                    quote->sub_snapshot(t, sm);
                }
                oir->routeRegister(trader);
                sms.emplace_back(sm);
                
            }
        }

        SS::env::trader->on_order([](const std::variant<trader::OrderRes, trader::CancelRes> &res) {
            
            // if(res.index() == 0)
            //     std::cout << __LINE__ << " " << mio::to_string(std::get<0>(res).time) << std::endl;
            // else
            //     std::cout << __LINE__ << " " << mio::to_string(std::get<1>(res).time) << std::endl;
            return oir->onOrder(res);
        });

        config.run(std::chrono::milliseconds(500));

        return 0;
    }
    int strategy_exit(int code){
        //std::cout tongji infromation
        config.stop();
        std::cout << "exit" << std::endl;
        
        // a();

        return 0;
    }
    int strategy_error(int code){
        return 0;
    }
    extern int strategy_main(int argc, char **argv);
}

int main(int argc, char **argv){
    return strategy_main(argc, argv);
}
