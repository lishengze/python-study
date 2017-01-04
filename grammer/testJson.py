import json

class Student(object):
    def __init__(self, name = 'Lee', age = 20, score = 'a'):
        self.name = name
        self.age = age
        self.score = score
        self.__dict__ = {
            'name': self.name,
            'age': self.age,
            'score': self.score,
            'friend': {
                'name': 'DC',
                'age': 15,
                'score': 'A'
            }
        }

def student2dict(obj):
    return {
        'name': obj.name,
        'age': obj.age,
        'score': obj.score
    }

tmpObj1 = Student('Tom', 25, 'B')
tmpObj2 = Student('Tom', 25, 'B')

# jsonObj = json.dumps(tmpObj, default = student2dict)
# jsonObj1 = json.dumps(tmpObj1, default = lambda obj:obj.__dict__)
# print jsonObj1
# print type(jsonObj1)

tmp1 = {
    'data': tmpObj1.__dict__
}

print (json.dumps(tmp1))