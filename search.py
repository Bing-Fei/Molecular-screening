import pandas as pd

data = pd.read_csv('data_proced.csv')

#这里列出的选项都可以在search里面使用
#其中除了functional_groups是非数值的，其他选项都是数值类的
options_list = ['HBA', 
               'HBD', 
               'TPSA', 
               'dipole', 
               'excitation_energy_1', 
               'excitation_energy_2', 
               'excitation_energy_3', 
               'excitation_energy_4', 
               'homo_energy', 
               'homo_lumo_gap', 
               'logP', 
               'lumo_energy', 
               'melting_point', 
               'molecular_refractivity', 
               'oscillator_strength_1', 
               'oscillator_strength_2', 
               'oscillator_strength_3', 
               'oscillator_strength_4', 
               'pccdb_id', 
               'molecular_mass', 
               'functional_groups']


#这是一个装饰器，用于实现函数批量处理数据，输入与输出都是pd.Serise对象
#函数将会逐个作用于serise中的每一个元素
#装饰器参数name是用来定义返回的serise的名字的
def pandasize(name):
    def pandasizer(func):
        def pandasized(serise,*args,**kargs):
            ret = []
            for item in serise:
                ret.append(func(item,*args,**kargs))
            return pd.Series(ret,name=name,index=serise.index)
        return pandasized
    return pandasizer

@pandasize('fg_filter')
def fg_filter(mol_fg,target_fgs):
    '''
    fg指官能团functional_group
    判断一个分子的官能团mol_fg是否包含所有目标官能团target_fgs
    '''
    #如果mol_fg是NaN,就直接返回False
    if pd.isna(mol_fg):return False
    #将单个target_fgs放入一个列表，避免报错
    if not isinstance(target_fgs,list):
        target_fgs = [target_fgs]
    #逐个匹配
    for target_fg in target_fgs:
        if target_fg not in mol_fg:
            return False
    return True 

def search(options):
    '''
    options是一个字典，包含了需要筛选的项目和筛选范围

    例：options = {'homo_lumo_gap' : (3,6),
                   'molecular_mass' : (100,None)}
    将会找出 3<=gap<=6 且 molecular_mass >=100 的分子

    例：options = {'functional_groups' : ['醇羟基','碳碳双键']}
    将会找出包含醇羟基和碳碳双键的分子

    '''
    ret = data
    for option,opRange in options.items():
        #先排除未知的筛选项
        if not option in options_list:
            print(f'unknown option {option}')
            continue

        #如果是官能团的筛选，要使用fg_filter函数进行筛选
        if option == 'functional_groups':
            ret = ret[fg_filter(ret['functional_groups'],opRange)]

        #非官能团的筛选
        else:
            if not len(opRange) == 2:
                print(f'range len should be 2,but len of {opRange} is {len(opRange)}')
                continue
            else:
                start,end = opRange[0],opRange[1]
                if start == None:
                    ret = ret[ret[option] <= end]
                elif end == None:
                    ret = ret[ret[option] >= start]
                else:
                    ret = ret[start <= ret[option]]
                    ret = ret[ret[option] <= end]

    return ret

print(search({
    'HBA' : (6,None), #HBA >=6
    'homo_lumo_gap' : (3,6), # 3 <= gap <= 6
    'molecular_mass' : (100,None), # mass >=100
    'functional_groups' : ['醇羟基','碳碳双键'] #包含这些官能团
}))    

