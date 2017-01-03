import json
class Student(object):
    def __init__(self, name = 'Lee', age = 20, score = 'a'):
        self.name = name
        self.age = age
        self.score = score
        self.__dict__ = {
            'name': self.name,
            'age': self.age,
            'score': self.score
        }
    
def student2dict(obj):
    return {
        'name': obj.name,
        'age': obj.age,
        'score': obj.score
    }

tmpObj1 = Student('Tom', 25, 'B')
tmpObj2 = Student('Tom', 25, 'B')

print type(tmpObj1)

# jsonObj = json.dumps(tmpObj, default = student2dict)
jsonObj1 = json.dumps(tmpObj1, default = lambda obj:obj.__dict__)
print jsonObj1
print type(jsonObj1)