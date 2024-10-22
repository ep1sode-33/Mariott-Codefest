from amadeus import Client, ResponseError
import csv

# Initialize Amadeus API client
amadeus = Client(
    client_id='bakcZl0m2Ke3Uhims3G7gPdcAfGhH2B1',
    client_secret='HvV7Ub1xLn62UGPe'
)

def ratingl(hotel_id: str):
    try:
        response = amadeus.e_reputation.hotel_sentiments.get(hotelIds=hotel_id)
        
        # Check if there's data and retrieve the rating
        if response.data and len(response.data) > 0:
            rating = response.data[0]['overallRating']
            print(f"Rating for hotel {hotel_id}: {rating}")
            return rating
        else:
            print(f"No rating data found for hotel {hotel_id}")
            return None
        
    except ResponseError as error:
        print(f"An error occurred: {error}")
        return None

def info(city: str):
    try:
        response = amadeus.reference_data.locations.hotels.by_city.get(cityCode=city)
        hotel_codes = [hotel['hotelId'] for hotel in response.data]
        # Debugging step: Check the format of the hotel codes
        print(f"Hotel codes for city {city}: {hotel_codes}")
        return hotel_codes
    except ResponseError as error:
        print(f"An error occurred: {error}")
        return None

def save(city: str, csv_filename: str):
    hotel_codes = info(city)
    if hotel_codes:
        with open(csv_filename, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Hotel ID', 'Location Sentiment'])
            for hotel_id in hotel_codes:
                rating = ratingl(hotel_id)
                if rating:
                    writer.writerow([hotel_id, rating])
                else:
                    writer.writerow([hotel_id, 'N/A'])
    else:
        print("No hotel codes found.")