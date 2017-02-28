class Animal(object):
    def __init__(self):
        self.animal_name = 'Dog'
    
    def GetAnimalName(self):
        print 'GetAnimalName'
        return self.animal_name

class Plant(object):
    def __init__(self):
        self.plant_name = 'maple'
    
    def GetPlantName(self):
        return self.plant_name

class People(Animal, Plant):
    def __init__(self, name = 'tmp'):
        self.name = name

    def output_name(self):
        print self.name
        print self.GetAnimalName()
        print self.GetPlantName()

Lee = People('Lee')
Lee.GetAnimalName()