import base64
import hashlib
import os
import sys
from time import time
from unittest import result
import orjson as json
import json as j
import io

from multiprocessing.pool import ThreadPool

class OurObject:
    """ The simple class for return json data as class object """
    def __init__(self, /, **kwargs):
        self.__dict__.update(kwargs)
    def __repr__(self):
        keys = sorted(self.__dict__)
        items = ("{}={!r}".format(k, self.__dict__[k]) for k in keys)
        return "{}({})".format(type(self).__name__, ", ".join(items))

    def __eq__(self, other):
        return self.__dict__ == other.__dict__


class finder:
    """make conditions for find elements"""
    def _is(OBJ , Value):
        """OBJ == Value"""
        _condition = {'obj' : OBJ , 'cond':'==' , 'value' : Value}
        return _condition
    def not_is(OBJ , Value):
        """OBJ != Value"""
        _condition = {'obj' : OBJ , 'cond':'!=' , 'value' : Value}
        return _condition
    def condition(OBJ , cond ,Value):
        """OBJ cond Value"""
        _condition = {'obj' : OBJ , 'cond':cond , 'value' : Value}
        return _condition
    def all():
        return {'obj' : '__all__' , 'cond' :'all' , 'value' : '___all___'}








class mkcond:
    """Apply conditions"""
    def __init__(self , finder) -> None:
        self.cond = finder['cond']
        self.val = finder['value']
        if self.val == '___all___':
            self.true = True
        else:
            self.true = False
    def test(self ,OBJ):
        if self.true:
            return True
        else:
            if type(OBJ) == str:
                OBJ = f'"{OBJ}"'
            if type(self.val) == str:
                # print(self.val)
                self.val = f'"{self.val}"'   
            exe = f'{OBJ} {self.cond} {self.val}'
            return eval(exe)


class connect:
    def __init__(self , db , compressed = False , cache = False ) -> None:
        """Welcome To the JingoDB :
param db = database name
param compressed = file indent handler
if True :
    indent == 2
else:
    indent == -1
"""     
        self.dir = '__jingodb__'
        try:
            os.mkdir('__jingodb__')
        except:
            pass
        if cache:
            self.data = {}
            self.checkType(True)
        else:
            if compressed == False:
                self.options = json.OPT_INDENT_2
            else:
                self.options = None
            self.db = db
            try:
                self.data = json.loads(open(db , 'rb').read())
            except:
                open(db , '+a').write('{}')
                self.data = json.loads(open(db , 'rb').read())
            self.checkType(False)

    def commit(self):
        """commit changes in database"""
        rand_file = io.FileIO(self.db, 'w')
        writer = io.BufferedWriter(rand_file,buffer_size=1)
        if self.options:
            j = json.dumps(self.data , option=self.options)
        else:
            j = json.dumps(self.data)
        writer.write(j)
        writer.flush()
        
    def getSize(self):
        """get size of datas in RAM"""
        return sys.getsizeof(self.data)
        
    def checkType(self , cache):
        """is JingoDB ? if not make it!"""
        if '__table__' not in self.data:
            self.data['__table__'] = {}
        if '__config__' not in self.data:
            self.data['__config__'] = {}
        if '__key__' not in self.data:
            self.data['__key__'] = {}
        if '__collection__' not in self.data:
            self.data['__collection__'] = {}
        if '__file__' not in self.data:
            self.data['__file__'] = {}
        if '__flood__' not in self.data:
            self.data['__flood__'] = {}
        if cache:
            return 0
        self.commit()
    def giveConfig(self , model):
        """returns an configuration as class object
param model = configuration name
        """
        __dict = self.data['__config__'][model]
        x = j.dumps(__dict)
        y = j.loads(x, object_hook=lambda d: OurObject(**d))
        return y

    def mkConfig(self ,model,exists = True):
        """Make new configuration with class model
param model = 
class test:
    def __init__(self):
        self.name = 'test'
        self.lname = 'ltest'
        self.__class__.__name__ = 'user'
result (in __config__ key):
user {
    "name" : "test",
    "lname" : "ltest"
}"""    
        dict_name = model.__class__.__name__
        if dict_name in self.data['__config__'] and exists == True:
            return False
        _dict = model.__dict__
        _id = len(self.data['__config__'])
        _dict.update({'__id__' : _id})
        self.data['__config__'][dict_name] = _dict

    def upConfig(self ,model,giveOBJ = None,**updates):
        """Update a configuration with classes or keywords
param model (optional)= 
class test:
    def __init__(self):
        self.name = 'test'
        self.lname = 'ltest'
        self.__class__.__name__ = 'user'

result (in __config__ key):
user {
    "name" : "test",
    "lname" : "ltest"
}
param updates (optional)=
name = 'test' , lname = 'ltest'

result (in __config__ key):
user {
    "name" : "test",
    "lname" : "ltest"
}
        """
        if giveOBJ:
            self.data['__config__'][model].update(giveOBJ.__dict__)
            
        else:
            
            self.data['__config__'][model].update(updates)


    def delConfig(self , model):
        """Delete configuration param model = configuration name"""
        self.data['__config__'].pop(model)
    
    def mkTable(self ,name,*columns , Exists = False):
        """Create new table 
param name = Table name
param *columns = 'col1' , 'col2' , 'col3' , ...
param Exists = if not exists if False : removes table and make new"""
        name = name.strip().replace(' ' , '_')
        
        if Exists == True:
            if name in self.data['__table__']:
                return 0
        
        table = self.data['__table__'][name]= []
        table.append({'__INFO__' : columns})
    
    def mkModelTable(self , model):
        dict_table = model.__dict__
        exists = dict_table['__exists__']
        dict_table.pop('__exists__')
        if exists == True:
            if model.__name__ in self['__table__']:return 0
        table = self.data['__table__'][model.__class__.__name__]= []
        lst = [i for i in dict_table]
        table.append({'__INFO__' : lst})

    

            

        

    def giveTable(self , name , obj , cond , value):
        table = self.data['__table__'][name]
        index = table[0]['__INFO__'].index(obj)
        table = table[1:]
        def key(obj):
            return obj[index]
        table.sort(key=key)
        cond = cond.strip()
        table_len = len(table)
        if cond == '>':
            if not table[0][index] > value:
                return None
        elif cond == '<':
            if not table[table_len-1][index] < value:
                return None
        if cond == '>':
            for i in table:
                if i[index] > value :
                    yield i
                else:
                    break
        elif cond == '<':
            table.reverse()
            for i in table:
                if i[index] < value :
                    yield i
                else:
                    break
        elif cond == '==':
            for i in table:
                if i[index] == value :
                    yield i
                if i[index] > value:
                    break

    def threadedGiveTable(self , name , obj , cond , value):
        pool = ThreadPool(processes=5000)
        async_result = pool.apply_async(self.giveTable, ( name , obj , cond , value)) 
        for i in async_result.get():
            yield i




    def upTable(self , __name__ , condition , **_set ):
        """update table
param condition = finder obj use finder.all() for all
param _set = set what for what
        """
        
        if condition['obj'] == '__all__':
            info = self.data['__table__'][__name__][0]['__INFO__']
            table = self.data['__table__'][__name__][1:]
            for i in table:
                for s in _set:
                    a = info.index(s)
                    i[a] = _set[s]
                    table[a] = i
        else:
            info = self.data['__table__'][__name__][0]['__INFO__']
            obj = info.index(condition['obj'])
            index = 0
            
            table = self.data['__table__'][__name__][1:]
            for i in table:
                a = mkcond(condition)
                if a.test(i[obj]):
                    for s in _set:
                       
                        a = info.index(s)
                        i[a] = _set[s]
                        table[a] = i
        self.data['__table__'][__name__] = [{'__INFO__' : info}] + table
        

    def inTable(self ,__table_name__ , *values,__model__ = None):
        """insert into table __table_name__
param model (optional)= 
class test:
    def __init__(self):
        self.name = 'test'
        self.lname = 'ltest'
        self.__class__.__name__ = 'user'

result (in __config__ key):
user {
    "name" : "test",
    "lname" : "ltest"
}
param values (optional)=
name = 'test' , lname = 'ltest'

result (in __config__ key):
user {
    "name" : "test",
    "lname" : "ltest"
}
        """
        if __model__:
            values = __model__
        table = self.data['__table__'][__table_name__]
        items = table[0]['__INFO__']
        lv = len(values)
        li = len(items)
        if lv != li:
            raise Exception (f'We have {li} value to supply but {lv} supplyed.')
        
        self.data['__table__'][__table_name__].append(values)


    def delRecord(self , table , condition=None , _id : int = None ):
        """delete record on table"""
        _table =  self.data['__table__'][table]
        info = _table[0]['__INFO__']
        _table = _table[1:]
        
        if _id :
            del self.data['__table__'][table][_id]
        else:
            if condition['obj'] == '__all__':
                for i in _table:
                    self.data['__table__'][table] = [{'__INFO__' : info}]
            else:
                obj = info.index(condition['obj'])
                for i in _table:
                    a = mkcond(condition)
                    if a.test(i[obj]):
                        
                        self.data['__table__'][table].remove(i)


    def delTable(self , table_name):
        """delete a table with name table_name"""
        self.data['__table__'][table_name] = {}
        self.data['__table__'].pop(table_name)

    def setkey(self , key , value):
        self.data['__key__'][key] = value
    def delKey(self , key):
        self.data['__key__'].pop(key)
    def giveKey(self , key):
        return self.data['__key__'][key]

    def collection(self , name):
        if name in self.data['__collection__']:
            return False
        self.data['__collection__'][name] = []
    
    def addDoc(self ,collection,doc):
        l = hashlib.sha256(str(len(self.data['__collection__'][collection])).encode())
        doc.update({'_id' : l.hexdigest()})
        self.data['__collection__'][collection].append(doc)
    
    def delDoc(self , collection , filters):
        d = self.data['__collection__'][collection]
        for i in d:
            for z in filters:
                a = d[i].get(filters[z] , ('is not in' , None))
                if a != ('is not in' , None):
                    self.data['__collection__'][collection][i] = {}
    
    def giveDoc(self , collection , filters):
        d = self.data['__collection__'][collection]
        for i in d:
            for z in filters:
                a = d[i].get(filters[z] , ('is not in' , None))
                if a != ('is not in' , None):
                    yield self.data['__collection__'][collection][i]
            if len(filters) == 0:
                yield from self.data['__collection__'][collection]

    def File(self ,name,byte):
        data = base64.b64encode(byte)
        self.data['__file__'][name] = data
    
    def delFile(self , name):
        self.data['__file__'].pop(name)
    
    def giveFile(self , name):
        return base64.b64decode(self.data['__file__'][name])
    
    def setFlood(self , value , s = 1 , m = 0 , h = 0 , d = 0):
        t = time()
        tn = t+s+(m*60)+(h*3600)+(d*86400)
        if t == tn:
            raise Exception ('please add some time')
        self.data['__flood__'][value] = tn
    
    def checkFlood(self , value , delete = True):
        t= time()
        if self.data['__flood__'][value] > t:
            if delete :
                self.data['__flood__'].pop(value)
            return False
        return True




def preModel(c , *a):
    _dict = c().__dict__
    return [_dict[i] for i in _dict]
