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
lista_gho_muerte_infantil = ['Number of deaths','Number of under-five deaths', 'Number of infant deaths']
lista_gho_muerte_adulta = ['Mortality rate for 5-14 year-olds (probability of dying per 1000 children aged 5-14 years)', 
'Adult mortality rate (probability of dying between 15 and 60 years per 1000 population)',
'Number of deaths attributed to non-communicable diseases, by type of disease and sex', 'Estimates of number of homicides',
'Estimated number of road traffic deaths','Mortality rate attributed to unintentional poisoning (per 100 000 population)','Crude suicide rates (per 100 000 population)']
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
                    if hijo.text in lista_gho_muerte_infantil:
                        gho = hijo.text
                        seguir = True
                        infantil = True
                    if hijo.text in lista_gho_muerte_adulta:
                        gho = hijo.text
                        seguir = True
                        adulto = True

                if seguir and hijo.tag == 'SEX':
                    sex = hijo.text


                if seguir and hijo.tag == 'YEAR':
                    year = hijo.text            

                if seguir and hijo.tag == 'Display':
                    display = hijo.text

                if seguir and hijo.tag == 'Numeric':
                    numeric = round(float(hijo.text))
                    if gho == 'Mortality rate for 5-14 year-olds (probability of dying per 1000 children aged 5-14 years)':
                        numeric = float(hijo.text)           
                if seguir and hijo.tag == 'High':
                    high = hijo.text

                if seguir and hijo.tag == 'Low':
                    low = hijo.text
                if seguir and numeric != '' and year != '' and sex!= '':
                    if infantil:
                        if (year, agegroup, sex, country, gho) in set_year_agegroup_sex_country_gho:
                            dic_año_edad[(year, agegroup, sex, country, gho)][0] += numeric
                        else:
                            set_year_agegroup_sex_country_gho.add((year, agegroup, sex, country, gho))
                            dic_año_edad[(year, agegroup, sex, country, gho)] = [numeric, ghecauses, display, high, low]
                    if adulto:
                        dic_año_edad[(year, agegroup, sex, country, gho)] = [numeric, ghecauses, display, high, low]


for llave in dic_año_edad.keys():
    lista_muertes_infantiles.append([llave[0], llave[1], llave[2], llave[3], llave[4],dic_año_edad[llave][0], dic_año_edad[llave][1], dic_año_edad[llave][2], dic_año_edad[llave][3], dic_año_edad[llave][4]])

df_muertes = pd.DataFrame(lista_muertes_infantiles, columns = ['year', 'agegroup', 'sex', 'country', 'gho', 'numeric', 'ghecauses', 'display', 'high', 'low'])


#print(df_muertes)
gc = gspread.service_account(filename='tarea-4-iic3103-316404-08700a821623.json')
sh = gc.open_by_key('1kSHQgnXHaLwyl4sSzi-PU88UeJc9-WgujOpjtAgWPvk')
hoja = sh.get_worksheet(2)

set_with_dataframe(hoja, df_muertes, resize=True)
