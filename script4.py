from numpy import format_float_scientific
import requests
import pandas as pd
import xml.etree.ElementTree as ET
import gspread
from gspread_dataframe import set_with_dataframe

r_chile = requests.get('http://tarea-4.2021-1.tallerdeintegracion.cl/gho_CHL.xml')
tree_chile = ET.fromstring(r_chile.content)

r_argentina = requests.get('http://tarea-4.2021-1.tallerdeintegracion.cl/gho_ARG.xml')
tree_argentina = ET.fromstring(r_argentina.content)

r_brasil = requests.get('http://tarea-4.2021-1.tallerdeintegracion.cl/gho_BRA.xml')
tree_brasil = ET.fromstring(r_brasil.content)

r_portugal = requests.get('http://tarea-4.2021-1.tallerdeintegracion.cl/gho_PRT.xml')
tree_portugal = ET.fromstring(r_portugal.content)

r_espana = requests.get('http://tarea-4.2021-1.tallerdeintegracion.cl/gho_ESP.xml')
tree_espana= ET.fromstring(r_espana.content)

r_gbr = requests.get('http://tarea-4.2021-1.tallerdeintegracion.cl/gho_GBR.xml')
tree_gbr = ET.fromstring(r_gbr.content)



dic_año_edad = {}
arboles = [tree_chile, tree_argentina, tree_brasil, tree_portugal, tree_espana, tree_gbr]
lista_muertes_infantiles = []
lista_gho = ['Mean BMI (kg/m&#xb2;) (crude estimate)', "Mean BMI (kg/m&#xb2;) (age-standardized estimate)",
"Prevalence of obesity among children and adolescents, BMI > +2 standard deviations above the median (crude estimate) (%)",
"Prevalence of obesity among adults, BMI &GreaterEqual; 30 (age-standardized estimate) (%)",
"Prevalence of overweight among children and adolescents, BMI > +1 standard deviations above the median (crude estimate) (%)",
"Prevalence of overweight among adults, BMI &GreaterEqual; 25 (age-standardized estimate) (%)",
"Prevalence of thinness among children and adolescents, BMI < -2 standard deviations below the median (crude estimate) (%)",
"Alcohol, recorded per capita (15+) consumption (in litres of pure alcohol)",
"Estimate of daily tobacco smoking prevalence (%)",
"Estimate of daily cigarette smoking prevalence (%)",
"Mean systolic blood pressure (crude estimate)",
"Mean Total Cholesterol (crude estimate)",
"Mean fasting blood glucose (mmol/l) (crude estimate)"]
set_year_agegroup_sex_country_gho = set()

for tree in arboles:
    for child in tree.iter('*'):
        if child.tag == 'Fact':
            country = ""
            sex = ""
            year = ""
            ghecauses = ""
            gho = ""
            agegroup = ""
            display = ""
            numeric = ""
            low = ""
            high = ""
            seguir = False
            infantil = False
            adulto = format_float_scientific
            for hijo in child.iter('*'):
                if hijo.tag == 'AGEGROUP':
                    agegroup = hijo.text

                if hijo.tag == 'COUNTRY':
                    country = hijo.text

                if hijo.tag == 'GHECAUSES':
                    ghecauses = hijo.text

                if hijo.tag == 'GHO':
                    if hijo.text in lista_gho or 'Prevalence of underweight' in hijo.text:
                        gho = hijo.text
                        seguir = True

                if seguir and hijo.tag == 'SEX':
                    sex = hijo.text

                if seguir and hijo.tag == 'YEAR':
                    year = hijo.text            

                if seguir and hijo.tag == 'Display':
                    display = hijo.text

                if seguir and hijo.tag == 'Numeric':
                    numeric = round(float(hijo.text))           
                if seguir and hijo.tag == 'High':
                    high = hijo.text

                if seguir and hijo.tag == 'Low':
                    low = hijo.text
                if seguir and numeric != '' and year != '' and sex!= '':
                    dic_año_edad[(year, agegroup, sex, country, gho)] = [numeric, ghecauses, display, high, low]


for llave in dic_año_edad.keys():
    lista_muertes_infantiles.append([llave[0], llave[1], llave[2], llave[3], llave[4],dic_año_edad[llave][0], dic_año_edad[llave][1], dic_año_edad[llave][2], dic_año_edad[llave][3], dic_año_edad[llave][4]])

df_muertes = pd.DataFrame(lista_muertes_infantiles, columns = ['year', 'agegroup', 'sex', 'country', 'gho', 'numeric', 'ghecauses', 'display', 'high', 'low'])


#print(df_muertes)
gc = gspread.service_account(filename='tarea-4-iic3103-316404-08700a821623.json')
sh = gc.open_by_key('1kSHQgnXHaLwyl4sSzi-PU88UeJc9-WgujOpjtAgWPvk')
hoja = sh.get_worksheet(3)

set_with_dataframe(hoja, df_muertes, resize=True)
