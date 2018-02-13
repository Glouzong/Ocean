# -*- coding: utf-8 -*-
# !/usr/bin/env python3
import random
from enum import Enum


class BadParametersError(Exception):
    pass


class cell(Enum):
    Victims = 1
    Predators = 2
    Barrage = 3
    Empty = 4


class Ocean(object):
    def __init__(self, sizeX, sizeY, show, timeDeath, timeNewVictims, timeNewPredators, endTime,
                 partVictims, partPredators, partEmpty, partBarrage):
        self.size_x = sizeX
        self.size_y = sizeY
        self.show = show  # show ocean
        self.time = 1
        self.timeDeath = timeDeath
        self.timeNewVictims = timeNewVictims
        self.timeNewPredators = timeNewPredators
        self.endTime = endTime
        self.partVictims = partVictims
        self.partPredators = partPredators
        self.partEmpty = partEmpty
        self.partBarrage = partBarrage
        self.generationOcean()

    def generationOcean(self):
        self.ocean = []
        self.predators = {}
        self.victims = set()
        self.populationPredators = []
        self.populationVictims = []
        for i in range(self.size_y):
            self.ocean.append([])
            for j in range(self.size_x):
                self.ocean[i].append(self.getCell())
                if self.ocean[i][j] == cell.Predators:
                    self.predators[(i, j)] = self.time - 1
                if self.ocean[i][j] == cell.Victims:
                    self.victims.add((i, j))
        self.populationPredators.append(len(self.predators))
        self.populationVictims.append(len(self.victims))

    def getCell(self):
        sum = self.partVictims + self.partPredators + self.partEmpty + self.partBarrage
        if sum < 1:
            raise BadParametersError(sum)
        temp = random.randint(1, sum)
        upperBound = self.partVictims
        if temp <= upperBound:
            return cell.Victims
        upperBound += self.partPredators
        if temp <= upperBound:
            return cell.Predators
        upperBound += self.partBarrage
        if temp <= upperBound:
            return cell.Barrage
        return cell.Empty

    def liveInOcean(self):
        if self.show:
            self.printOcean()
        while len(self.predators) > 0 and len(self.victims) > 0 and self.time < self.endTime:
            self.moveInOcean()
            if self.time % self.timeDeath == 0:
                self.deathInOcean()
            if self.time % self.timeNewPredators == 0:
                self.getNewPredators()
            if self.time % self.timeNewVictims == 0:
                self.getNewVictims()
            self.time += 1
            if self.show:
                self.printOcean()
            self.populationPredators.append(len(self.predators))
            self.populationVictims.append(len(self.victims))
        if self.show:
            self.printOcean()
        return self.populationVictims, self.populationPredators

    def moveInOcean(self):
        tempIteration = set(self.victims)
        for i in tempIteration:
            if self.ocean[i[0]][i[1]] == cell.Victims:
                newCage = self.getNextCage(i[0], i[1], cell.Victims)
                if newCage is not None:
                    self.ocean[i[0]][i[1]] = cell.Empty
                    self.victims.remove(i)
                    self.ocean[newCage[0]][newCage[1]] = cell.Victims
                    self.victims.add(newCage)
            else:
                self.victims.remove(i)

        tempIteration = dict(self.predators)
        for i in tempIteration:
            newCage = self.getNextCage(i[0], i[1], cell.Predators)
            if newCage is not None:
                self.ocean[i[0]][i[1]] = cell.Empty
                if self.ocean[newCage[0]][newCage[1]] == cell.Victims:
                    self.predators[newCage] = self.time
                    self.victims.remove(newCage)
                else:
                    self.predators[newCage] = self.predators[i]
                self.ocean[newCage[0]][newCage[1]] = cell.Predators
                self.predators.pop(i)

    def getNextCage(self, item_x, item_y, typeCage):
        nextCage = []
        if item_x - 1 >= 0:
            temp = self.ocean[item_x - 1][item_y]
            if temp == cell.Empty or (typeCage == cell.Predators and temp == cell.Victims):
                nextCage.append((item_x - 1, item_y))
        if item_x + 1 < len(self.ocean):
            temp = self.ocean[item_x + 1][item_y]
            if temp == cell.Empty or (typeCage == cell.Predators and temp == cell.Victims):
                nextCage.append((item_x + 1, item_y))

        if item_y - 1 >= 0:
            temp = self.ocean[item_x][item_y - 1]
            if temp == cell.Empty or (typeCage == cell.Predators and temp == cell.Victims):
                nextCage.append((item_x, item_y - 1))
        if item_y + 1 < len(self.ocean[0]):
            temp = self.ocean[item_x][item_y + 1]
            if temp == cell.Empty or (typeCage == cell.Predators and temp == cell.Victims):
                nextCage.append((item_x, item_y + 1))

        if len(nextCage) == 0:
            return
        return random.choice(nextCage)

    def printOcean(self):
        print(self.time, "________________________")
        for i in self.ocean:
            for j in i:
                if j == cell.Empty:
                    print('0', end=' ')
                if j == cell.Predators:
                    print('P', end=' ')
                if j == cell.Victims:
                    print('V', end=' ')
                if j == cell.Barrage:
                    print('B', end=' ')
            print()

    def deathInOcean(self):
        tempIteration = dict(self.predators)
        for i in tempIteration:
            if self.time - self.predators[i] >= self.timeDeath:
                self.ocean[i[0]][i[1]] = cell.Empty
                self.predators.pop(i)

    def getNewPredators(self):
        tempIteration = dict(self.predators)
        for i in tempIteration:
            temp = self.getNextCage(i[0], i[1], cell.Predators)
            if temp is None:
                continue
            if self.ocean[temp[0]][temp[1]] == cell.Victims:
                self.victims.remove(temp)
            self.predators[temp] = self.time
            self.ocean[temp[0]][temp[1]] = cell.Predators

    def getNewVictims(self):
        tempIteration = set(self.victims)
        for i in tempIteration:
            temp = self.getNextCage(i[0], i[1], cell.Victims)
            if temp is None:
                continue
            self.victims.add(temp)
            self.ocean[temp[0]][temp[1]] = cell.Victims


if __name__ == '__main__':
    try:
        test = Ocean(10, 10, True, 30, 20, 50, 100, 20, 10, 40, 30)
        test.liveInOcean()
    except BadParametersError:
        print("Bad parameters")
