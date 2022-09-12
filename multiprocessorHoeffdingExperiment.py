'''



'''

import numpy as np
import pandas as pd
import altair as alt
import concurrent.futures
from functools import wraps
from enum import Enum
from typing import Literal
from random import randrange

class CoinSides(Enum):
    HEAD = 0
    Tail = 1


class FairCoin:
    def __init__(self) -> None:
        self._numHeads = 0
        self._numTails = 0
        self._head_vs_tails_probability = 0.5

    def _processFlip(self, coinSide: Literal[0, 1]) -> None:
        if coinSide == CoinSides.HEAD.value:
            self._numHeads += 1
        elif coinSide == CoinSides.Tail.value:
            self._numTails += 1
    
    def flip(self) -> Literal[0, 1]:
        numOfFlips = 1
        # Binomial Distribution should return a scalar value of 0 | 1
        results: Literal[0, 1] = np.random.binomial(numOfFlips, self._head_vs_tails_probability)
        self._processFlip(results)
        return results
    
    def headFrequency(self) -> float:
        totalCoinFlips = self._numHeads + self._numTails
        return self._numHeads / totalCoinFlips

    def tailFrequency(self) -> float:
        totalCoinFlips = self._numHeads + self._numTails
        return self._numTails / totalCoinFlips

class CoinFlipper:
    def __init__(self) -> None:
        self._coins: dict[Literal["firstCoin", "randomCoin", "minCoin"], FairCoin | None] = self._defaultCoins()

    def getCoins(self):
        return self._coins
    
    def _defaultCoins(self) ->  dict[Literal["firstCoin", "randomCoin", "minCoin"], FairCoin | None]:
        return {
            "firstCoin": None,
            "randomCoin": None,
            "minCoin": None,
        }
    
    def _randomCoinToPick(self, numOfCoins: int) -> int:
        '''
        numOfCoins: int
                integer of coins to choose from. range is [0, numOfCoins)

        ### returns: 
        Literal[0, numOfCoins - 1]
                returns a random number that will map to the coin that should used be for self._coins["randomCoin"]

                Note return value of 0 means the first coin and  (numOfCoins - 1) means coin number equal to numOfCoins
        '''
        return randrange(0, numOfCoins)
    
    def flipCoins(self, sideFrequencyToTrack: CoinSides, numOfCoins: int, flipsPerCoin: int):
        randomCoinNum = self._randomCoinToPick(numOfCoins)
        for coinNum in range(numOfCoins):
            coin = FairCoin()
            if coinNum == 0:
              self._coins["firstCoin"] = coin
            if self._coins["randomCoin"] is None and coinNum == randomCoinNum:
                self._coins["randomCoin"] = coin
            
            for flipNum in range(flipsPerCoin):
                coin.flip()
            if self._coins["minCoin"] is None or coin.headFrequency() < self._coins["minCoin"].headFrequency():
                self._coins["minCoin"] = coin


def _coinFlipHelper(numOfCoins: int, flipsPerCoin: int, printI: int) -> CoinFlipper:
    print(f"iteration = {printI}")
    coinFlipper = CoinFlipper()
    coinFlipper.flipCoins(CoinSides.HEAD, numOfCoins, flipsPerCoin)
    return coinFlipper

def multiprocessorHoeffdingExperiment(iterations: int, numOfCoins: int, flipsPerCoin: int):
        coinHeadsFrequencies: dict[Literal["firstV", "randomV", "minV"], list[float]] = {
        "firstV": [],
        "randomV": [],
        "minV": [],
        }

        with concurrent.futures.ProcessPoolExecutor() as executor:
            results = [executor.submit(_coinFlipHelper, numOfCoins, flipsPerCoin, i) for i in range(iterations)]

            for f in concurrent.futures.as_completed(results):
                coinHeadsFrequencies["firstV"].append(f.result().getCoins()["firstCoin"].headFrequency())
                coinHeadsFrequencies["randomV"].append(f.result().getCoins()["randomCoin"].headFrequency())
                coinHeadsFrequencies["minV"].append(f.result().getCoins()["minCoin"].headFrequency())
        return coinHeadsFrequencies


def main():
    # vFullDistributions = runHoeffdingInequalityExperiment(100000, 1000, 10)
    vFullDistributions = multiprocessorHoeffdingExperiment(100000, 1000, 10)

    v1 = np.array(vFullDistributions["firstV"])
    vRand = np.array(vFullDistributions["randomV"])
    vMin = np.array(vFullDistributions["minV"])

    v1Avg = np.mean(v1)
    vRandAvg = np.mean(vRand)
    vMinAvg = np.mean(vMin)


    print(f"##########################\n")
    print(f"##### printing averages... ######")
    print(f"{v1Avg = }")
    print(f"{vRandAvg = }")
    print(f"{vMinAvg = }")
    '''
    v1Avg = 0.49955099999999997
    vRandAvg = 0.4992469999999999
    vMinAvg = 0.037892999999999996
    '''

    # np.savetxt("v1.csv", v1, delimiter=",")
    # np.savetxt("vRand.csv", vRand, delimiter=",")
    # np.savetxt("vMin.csv", vMin, delimiter=",")

if __name__ == "__main__":
    main()