import credentials
import asyncio
import logging
import aiohttp
import mysql.connector as mariadb
from mysql.connector import Error
import pyfronius

results = []
selectedResults = {}

datapoints = ["co2_factor",
              "cash_factor",
              "delivery_factor",
              "energy_day",
              "energy_total",
              "energy_year",
              "power_grid",
              "power_load",
              "power_photovoltaics",
              "relative_autonomy",
              "relative_self_consumption",
              "power_real_phase_1",
              "power_real_phase_2",
              "power_real_phase_3",
              "power_real",
              "energy_real_consumed",
              "energy_real_produced",
              "voltage_dc",
              "current_dc"]

async def getFroniusData(loop, host):
    global results

    timeout = aiohttp.ClientTimeout(total=10)
    async with aiohttp.ClientSession(loop=loop, timeout=timeout) as session:
        fronius = pyfronius.Fronius(session, host)

        # use the optional fetch parameters to configure
        # which endpoints are acessed
        # NOTE: configuring the wrong devices may cause Exceptions to be thrown
        res = await fronius.fetch(
            active_device_info=False,  # list of inverters, meters
            inverter_info=False,  # Vpp max, names, info, error code
            logger_info=True,  # konstanten
            power_flow=True,  # energy_day/year, power_grid/load/pv, autonomy, consumption
            system_meter=False,  # phase, vulatage of each meter
            system_inverter=True,  # energy_day/year/total
            system_ohmpilot=False,
            system_storage=True,
            device_meter=["0"],  # das sind die eizelnen phase daten =["0"]
            # storage is not necessarily supported by every fronius device
            device_storage=[],
            device_inverter=["1"],
            loop=loop,
        )
        results.extend(res)


def printAll():
    for r in results:
        print("#" * 60)
        # print(json.dumps(r, indent=4))

        for topic in r:
            if topic in datapoints:
                name = "* " + topic
            else:
                name = "  " + topic
            try:
                space = " " * (32 - len(name))
                print(name, end=space)
                print(r[topic]['value'], end=" ")
                print(r[topic]['unit'])
            except:
                print()


def selectTopics():
    for r in results:
        for topic in r:
            if topic in datapoints:
                try:
                    value = r[topic]['value']
                    unit = r[topic]['unit']
                    if value is not None:
                        selectedResults[topic] = (value, unit)
                except:
                    pass
            else:
                name = "  " + topic


def printSelected():
    for i in selectedResults:
        space = " " * (32 - len(i))
        print(i, end=space)
        print(selectedResults[i][0], end=" ")
        print(selectedResults[i][1])


def uploadDB():
    try:
        connection = mariadb.connect(host=credentials.host, user=credentials.user, port=credentials.port, password=credentials.password)
    except Error as e:
        print("Error while connecting to MySQL", e)

    if connection.is_connected():
        cursor = connection.cursor()
        print(f"connected to: {credentials.user}@{credentials.host}:{credentials.port}")
        cursor.execute(f"use {credentials.scheme};")

        execstring = f"INSERT INTO `{credentials.table}` (`timestamp`,"
        for i in selectedResults:
            execstring += ("`" + i + "`, ")
        execstring = execstring[:-2]
        execstring += (") VALUES (CURRENT_TIME(), ")
        for i in selectedResults:
            execstring += ("" + str(selectedResults[i][0]) + ", ")
        execstring = execstring[:-2]
        execstring += (");")

        print(execstring)
        cursor.execute(execstring)
        connection.commit()
        connection.close()


def main():
    logging.basicConfig(level=logging.INFO)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(getFroniusData(loop, credentials.fronius_ip_address))

    printAll()
    selectTopics()
    printSelected()
    uploadDB()


if __name__ == "__main__":
    main()
