from rdkit.Chem import Descriptors
from rdkit.Chem import MolFromSmiles,MolFromSmarts
import pandas as pd
'''
    用于给数据新增两列：一列是官能团，一列是相对分子质量
'''

#这是一个装饰器，用于实现函数批量处理输出，输入与输出都是pd.Serise对象
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


# 该函数得到过chatGPT帮助:D 
@pandasize('functional_groups') #用pandasize装饰，使得输入输出可以使用pandas一维数组serise
def find_functional_groups(smiles):
    # 使用 RDKit 从 SMILES 字符串生成分子对象
    mol = MolFromSmiles(smiles)
    
    if not mol:
        return "无效的SMILES字符串"
    
    # 获取分子中的所有子结构
    functional_groups = []
    
    # 扩展的SMARTS表达式字典，包含更多常见官能团
    # 数据来源https://daylight.com/dayhtml_tutorials/languages/smarts/smarts_examples.html
    smarts_dict = {
        '碳碳双键' : '[$([CX3]=[CX3])]',
        '碳碳三键' : '[$([CX2]#C)]',
        '酰卤基' : '[CX3](=[OX1])[F,Cl,Br,I]',
        '醛基' : '[CX3H1](=O)[#6]',
        '酸酐' : '[CX3](=[OX1])[OX2][CX3](=[OX1])',
        '酰胺基' : '[NX3][CX3](=[OX1])[#6]',
        '羧基' : '[CX3](=O)[OX2H1]',
        '氰胺基' : '[NX3][CX2]#[NX1]',
        '氰基': '[NX1]#[CX2]',
        '酯基' : '[#6][CX3](=O)[OX2H0][#6]',
        '酮基' : '[#6][CX3](=O)[#6]',
        '醚键' : '[OD2]([#6])[#6]',
        '硝基' : '[$([NX3](=O)=O),$([NX3+](=O)[O-])][!#8]',
        '亚硝基' : '[NX2]=[OX1]',
        '醇羟基' : '[#6][OX2H]',
        '酚羟基' : '[OX2H][cX3]:[c]',
        '磷羟基' : '[OX2H]P',
        '过氧基' : '[OX2,OX1-][OX2,OX1-]',
        '卤原子' : '[#6][F,Cl,Br,I]'
    }
    # 检查常规官能团的匹配
    for group_name, smarts in smarts_dict.items():
        # 通过SMARTS表达式查找匹配的官能团
        pattern = MolFromSmarts(smarts)
        if mol.HasSubstructMatch(pattern):
            functional_groups.append(group_name)
    
    return '-'.join(functional_groups)

@pandasize('molecular_mass') #同上
def get_MolWt(smiles):
    # 使用 RDKit 从 SMILES 字符串得到该分子的相对分子质量
    mol = MolFromSmiles(smiles)
    try:
        mol_weight = Descriptors.MolWt(mol)
    except:
        mol_weight = -1
    return mol_weight

data = pd.read_csv('data_raw.csv')
data_smiles = data['smiles']
data_MolWt = get_MolWt(data_smiles)
data_functional_groups = find_functional_groups(data_smiles)
data = pd.concat([data,data_MolWt,data_functional_groups],axis=1)
print(data)
_ = input("savd the processed data? If so,enter 'yes'")
if _ == 'yes':data.to_csv('data_proced.csv',index=False)