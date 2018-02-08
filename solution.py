
# coding: utf-8

# In[27]:


import re


# In[24]:


def baseconvert(n, base):
    """convert positive decimal integer n to equivalent in another base (2-36)"""
    
    returnMe = [];
    
    try:
        n = int(n)
        base = int(base)
    except:
        return ""

    if n < 0 or base < 2 or base > 36:
        return ""

    while 1:
        r = n % base
        returnMe.append(r)
        n = n // base
        if n == 0:
            break

    return returnMe


# In[94]:


class Rule():
    def __init__(self, transformMe, replace, possibilities):
        self.transformMe = transformMe
        self.indices = [m.start() for m in re.finditer(replace, transformMe)]
        possibilities.insert(0, replace)
        self.possibilities = possibilities
        self.replace = replace
        self.maxTransformations = len(self.possibilities) ** len(self.indices)

        
    def getMaxTransformations(self):
        return self.maxTransformations;
    
    def getTransformation(self, i):
        transformationArray = baseconvert(i, len(self.possibilities));
        
        while(len(transformationArray) < len(self.indices) ):
            transformationArray.append(0)

        i = 0;
        returnMe = self.transformMe
        offset = 0
        for index in self.indices:
            returnMe = returnMe[:index+offset] + self.possibilities[transformationArray[i]] +  returnMe[index+offset+len(self.replace):]
            offset += len(self.possibilities[transformationArray[i]]) - len(self.replace)
            i+=1;
        return returnMe


# In[95]:


r  = Rule("anan","an",["4321", "@"])


# In[96]:


for k in range(0,r.getMaxTransformations()):
    print(r.getTransformation(k))


# In[61]:




