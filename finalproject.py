import arcpy
import csv
import sys

#list of European countries from https://stevendobbelaerebe.wordpress.com/2009/03/03/array-with-a-list-of-european-countries/
#list is for filtering out all the countries in the world to just European countries
europeanCountries = ["Albania", "Andorra", "Armenia", "Austria", "Azerbaijan", "Belarus", "Belgium", "Bosnia and Herzegovina", "Bulgaria", "Croatia", "Cyprus", "Czech Republic", "Denmark", "Estonia", "Finland", "France", "Georgia", "Germany", "Greece", "Hungary", "Iceland", "Ireland", "Italy", "Kosovo", "Latvia", "Liechtenstein", "Lithuania", "Luxembourg", "Macedonia", "Malta", "Moldova", "Monaco", "Montenegro", "The Netherlands", "Norway", "Poland", "Portugal", "Romania", "Russia", "San Marino", "Serbia", "Slovakia", "Slovenia", "Spain", "Sweden", "Switzerland", "Turkey", "Ukraine", "United Kingdom", "Vatican City"]
#countries.csv file from https://developers.google.com/public-data/docs/canonical/countries_csv
#read the countries.csv file and transfer the data into a list
with open('countries.csv', 'r') as file:
    coordinates = csv.reader(file)
    coordinatesData = list(coordinates)
#population-density.csv file from https://ourworldindata.org/grapher/population-density
#revises the population-density.csv so the data pool is smaller
with open('population-density.csv', 'r') as input, open('population-density-revised.csv', 'w', newline='', encoding='utf-8') as output:
    writer = csv.writer(output)
    #writes the first row without condition statement because it's just titles
    writer.writerow(next(csv.reader(input)) + coordinatesData[0])
    #nested for loops that go through the coordinates (countries.csv) list and csv input
    for row1 in csv.reader(input):
        for row2 in coordinatesData:
            #if the country name is in the list of european countries
            #if the country names are same in both groups (for adding correct latitude and longitude)
            #if the row has an ISO code, so it doesn't add continent data
            #filters down the list of years so its the current year of 2023 and the past twenty years
            if (row1[0] in europeanCountries) and (row1[0] == row2[3]) and (row1[1] != "") and (int(row1[2]) >= 2003) and (int(row1[2]) <= 2023):
                writer.writerow(row1 + row2)
input.close()
output.close()
#csv fields for population-density-revised.csv
csvField_LAT = "latitude"
csvField_LON = "longitude"
csvField_NAME = "Entity"
csvField_YEAR = "Year"
csvField_POPD = "Population density"
#desired shapefile fields
shpField_ID = "id"
shpField_NAME = "country"
shpField_YEAR = "year"
shpField_POPD = "density"

ROOT_DIRECTORY = "C:\\Temp\\"
#WGS84 for spatial reference
WGS_84_Info = r'GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137.0,298.257223563]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]]'
f = open(ROOT_DIRECTORY + "WGS_84.prj", "w")
f.write(WGS_84_Info)
f.close()

#creates the shapefile with desired shapefile fields
arcpy.env.overwriteOutput = True
Output_Shapefile_FeatureClass = arcpy.CreateFeatureclass_management(ROOT_DIRECTORY, "pop_den.shp", "POINT","","DISABLED","DISABLED",ROOT_DIRECTORY + "WGS_84.prj")
arcpy.AddField_management(Output_Shapefile_FeatureClass, shpField_NAME, "TEXT", field_length=255)
arcpy.AddField_management(Output_Shapefile_FeatureClass, shpField_YEAR, "LONG", 9)
arcpy.AddField_management(Output_Shapefile_FeatureClass, shpField_POPD, "DOUBLE")
#parses the data from the revised csv to the new shapefile
file_in = ROOT_DIRECTORY + 'population-density-revised.csv'
with open(file_in) as csvfile:
    current_data = csv.DictReader(csvfile)
    rowidval = 0
    for row in current_data:
        try:
            fields = ['SHAPE@XY',shpField_NAME,shpField_YEAR,shpField_POPD,shpField_ID]
            cursor = arcpy.da.InsertCursor(Output_Shapefile_FeatureClass, fields)
            xy = (float(row[csvField_LON]), float(row[csvField_LAT]))
            cursor.insertRow((xy, row[csvField_NAME],row[csvField_YEAR],float(row[csvField_POPD]),rowidval))
            rowidval += 1
        except Exception:
            e = sys.exc_info()[1]
            print(e.args[0])
del cursor
print("FINISHED")