""" Weather provider.
"""

import re
import html
from bs4 import BeautifulSoup

from weatherapp.sinoptik import config
from weatherapp.core.abstract import WeatherProvider


class SinoptikProvider(WeatherProvider):
    """ Weather provider for AccuWeather site.
    """

    name = config.SINOPTIK_PROVIDER_NAME
    title = config.SINOPTIK_PROVIDER_TITLE

    def get_default_location(self):
        """ Default location name.
        """
        return config.DEFAULT_SINOPTIK_LOCATION_NAME

    def get_default_url(self):
        """ Default location url.
        """
        return config.DEFAULT_SINOPTIK_LOCATION_URL

    def get_name(self):
        """ Get name provider
        """
        return self.name

    def get_link_continent(self):
        """ Get location country.
        """

        soup = BeautifulSoup(self.get_page_source
                             (config.SINOPTIK_BROWSE_LOCATIONS), 'html.parser')
        container_continent = \
            soup.find('div', attrs={'style': 'font-size:12px;'})
        continent_link = container_continent.find_all("a")
        list_continent = []
        for link in continent_link:
            url = link.get('href')
            location = link.get_text()
            list_continent.append((location, url))
        return list_continent

    def get_link_country(self, location_url):
        """ Get location city.
        """

        country_tag = \
            BeautifulSoup(self.get_page_source(location_url), 'html.parser')
        container_city = country_tag.find(class_="maxHeight")
        city_link = container_city.find_all("a")
        list_country = []
        for link in city_link:
            url = link.get('href')
            location = link.get_text()
            list_country.append((location, url))
        return list_country

    def configurate(self):
        """ The user chooses the city for which he wants to get the weather.
        """
        # Find continent
        list_continent = self.get_link_continent()
        for index, location in enumerate(list_continent):
            print("{}. {}".format((index + 1), (location[0])))
        while True:
            try:
                index_continent =\
                    int(input('Please select continent location: '))
                if index_continent > 0:
                    link_continent = list_continent[index_continent - 1]
                    break
            except ValueError:
                print("That was no valid number. Try again...")
            except IndexError:
                print("This number out of range. Try again...")

        continent_url = 'http:' + link_continent[1]

        # find counrty
        list_country = self.get_link_country(continent_url)
        for index, location in enumerate(list_country):
            print("{}. {}".format((index + 1), (location[0])))
        while True:
            try:
                index_country =\
                    int(input('Please select country location: '))
                if index_country > 0:
                    link_country = list_country[index_country - 1]
                    break
            except ValueError:
                print("That was no valid number. Try again...")
            except IndexError:
                print("This number out of range. Try again...")

        country_url = 'http:' + link_country[1]

        # Find region
        list_region = self.get_link_country(country_url)
        for index, location in enumerate(list_region):
            print("{}. {}".format((index + 1), (location[0])))
        while True:
            try:
                index_region = int(input('Please select region location: '))
                if index_region > 0:
                    link_region = list_region[index_region - 1]
                    break
            except ValueError:
                print("That was no valid number. Try again...")
            except IndexError:
                print("This number out of range. Try again...")

        location_region = 'http:' + link_region[1]

        # Find city
        page_city = \
            BeautifulSoup(self.get_page_source(location_region), 'html.parser')
        container_tag = page_city.find(class_="mapBotCol")
        city_tag = container_tag.find(class_="clearfix")
        list_city = []
        for link in city_tag.find_all('a'):
            url = 'http:' + link.get('href')
            location = link.get_text()
            list_city.append((location, url))
        for index, location in enumerate(list_city):
            print("{}. {}".format((index + 1), (location[0])))
        while True:
            try:
                index_city = int(input('Please select city location: '))
                if index_city > 0:
                    city = list_city[index_city - 1]
                    break
            except ValueError:
                print("That was no valid number. Try again...")
            except IndexError:
                print("This number out of range. Try again...")

        self.save_configuration(*city)

    def get_weather_info(self, page):
        """ The function returns a list with the value the state of the weather.
        """

        # create a blank dictionary to enter the weather data
        weather_info = {}
        soup = BeautifulSoup(page, 'html.parser')
        container_tag = soup.find(id="bd1c")

        if self.app.options.tomorrow == 'tomorrow':
            container_tag = soup.find(id="bd2")
            if container_tag:
                tomorrow_temp_min = \
                    container_tag.find(class_="min").get_text()
                tomorrow_temp_max = \
                    container_tag.find(class_="max").get_text()
                if tomorrow_temp_min or tomorrow_temp_max:
                    weather_info['temp'] = tomorrow_temp_min + '.. ' +\
                        tomorrow_temp_max

                cond_info = \
                    container_tag.find(class_="weatherIco").attrs["title"]
                if cond_info:
                    weather_info['cond'] = cond_info

                tomorrow_day_url = 'http:' + container_tag.find('a').attrs['href']
                if tomorrow_day_url:
                    tomorrow_day = self.get_page_source(tomorrow_day_url)
                    tomorrow_day_page = BeautifulSoup(tomorrow_day,
                                                      'html.parser')
                    container_tag_wind = tomorrow_day_page.find(class_="rSide")
                    wind_tag = container_tag_wind.find(class_="weatherDetails")

                    lst = []
                    for info in wind_tag.find_all(class_="gray"):
                        current_info = info.find('td', attrs={'class': 'p5'})
                        tooltip_wind = current_info.find(class_="Tooltip")
                        lst.append(tooltip_wind)
                    if lst:
                        weather_info['wind'] = lst[-1].attrs['data-tooltip']

        elif self.app.options.regexp:
            tag_temp = re.compile(r"(?is)<p class=\"today-temp\"[^>]*>(.+?)[?</p>]")
            today_temp = tag_temp.findall(page)
            if today_temp:
                weather_info['temp'] = html.unescape(today_temp[0])

            container_realfeel = re.compile(r"(?is)<tr class=\"temperatureSens\"[^>]*>(.+?)</tr>")
            realfeel_info = container_realfeel.findall(page)
            tag_realfeel = re.compile(r"(?is)<td class=\"[a-z] |cur\"[^>] *>(.+?)</td>")
            realfeel_info = str(realfeel_info)
            realfeel = tag_realfeel.findall(realfeel_info)
            if realfeel:
                weather_info['feels_like'] = html.unescape(realfeel[0])

            tag_cond = re.compile(r"(?is)id=\"bd1\"[^>]*>(.+?)</div>")
            cond_container = re.search(tag_cond, page)
            cond_info = re.compile(r"(?is)<div class=\"weatherIco \w+?\" title=.(.+?)[$\">]")
            cond = cond_info.findall(cond_container.group())
            if cond:
                weather_info['cond'] = cond[0]

            tag_cont_wind = re.compile(r"(?is)<tr class=\"gray\"[^>]*>(.+?)</tr>")
            container_wind = tag_cont_wind.findall(page)
            tag_wind = re.compile(r"(?is)<td class=\"[a-z] |cur\"[^>] *>(.+?)</td>")
            lst_wind = tag_wind.findall(str(container_wind))
            wind_info = re.compile(r"(?is)<div data-tooltip=\"(.*?)[\"]")
            wind = wind_info.findall(str(lst_wind))
            if wind:
                weather_info['wind'] = wind[0]
        else:
            if container_tag:
                today_temp = \
                    container_tag.find("p", class_="today-temp").get_text()
                if today_temp:
                    weather_info['temp'] = today_temp
                realfeel_info = container_tag.find(class_="temperatureSens")
                realfeel = realfeel_info.find(class_="cur").get_text()
                if realfeel:
                    weather_info['feels_like'] = realfeel
                cond_info = \
                    container_tag.find(class_="weatherIco").attrs["title"]
                if cond_info:
                    weather_info['cond'] = cond_info
                wind_tag = container_tag.find(class_="weatherDetails")
                lst = []
                for info in wind_tag.find_all(class_="gray"):
                    current_info = info.find('td', attrs={'class': 'cur'})
                    tooltip_wind = current_info.find(class_="Tooltip")
                    lst.append(tooltip_wind)
                if lst:
                    weather_info['wind'] = lst[-1].attrs['data-tooltip']

        return weather_info
