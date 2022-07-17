from functools import reduce
from torch import layer_norm
from tqsdk import TqApi, TqAuth, TargetPosTask

api = TqApi(auth=TqAuth("15221624883", "15221shuai"))

grid_region_long = [0.005]*10
grid_region_short = [0.005]*10
grid_volume_long = [i for i in range(11)]
grid_volume_short = [i for i in range(11)]
grid_prices_long = [reduce(lambda p,r:p*(1-r), grid_prices_long[:i], 8750) for i in range(11)]
gird_prices_short = [reduce(lambda p,r:p*(1+r), grid_region_short[:i], 8750) for i in range(11)]

quote = api.get_quote("DCE.p2209")
target_pos = TargetPosTask(api, "DCE.p2209")
position = api.get_position("DCE.p2209")

def wait_price(layer):
    if layer > 0 or quote.last_price <= grid_prices_long[1]:
        while True:
            api.wait_update()
            if layer < 10 and quote.last_price <= grid_prices_long[layer+1]:
                target_pos.set_target_volume(grid_volume_long[layer+1])
                wait_price(layer+1)
                target_pos.set_target_volume(grid_prices_long[layer+1])
    elif layer < 0 or quote.last_price >= gird_prices_short[1]:
        layer = -layer
        while True:
            api.wait_update()
            if layer < 10 and quote.last_price >= gird_prices_short[layer+1]:
                target_pos.set_target_volume(-grid_volume_short[layer+1])
                wait_price(-(layer+1))
                if layer < 10 and quote.last_price >= gird_prices_short[layer+1]:
                    target_pos.set_target_volume(-grid_volume_short[layer+1])
                    wait_price(-(layer+1))
                    target_pos.set_target_volume(-grid_volume_short[layer+1])
                if quote.last_price < gird_prices_short[layer]:
                    return

while True:
    api.wait_update()
    wait_price()
    target_pos.set_target_volume(0)           
     
