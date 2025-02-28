from geoip2.database import Reader
from django.conf import settings

def get_location_from_ip(ip):
    try:
        reader = Reader(settings.GEOIP_PATH)
        response = reader.city(ip)
        city = response.city.name if response.city.name else ""
        country = response.country.name if response.country.name else ""
        # latitude = response.location.latitude
        # longitude = response.location.longitude

        location_parts = []
        if city:
            location_parts.append(city)
        if country:
            location_parts.append(country)
        # if latitude is not None and longitude is not None:
        #     location_parts.append(f"{latitude}, {longitude}")

        location_text = ", ".join(location_parts)
        return location_text
    except Exception as e:
        print(f"GeoIP2 error: {e}")
        return "Location could not be determined."
