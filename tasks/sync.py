import logging
from datetime import datetime
from tasks.celery_worker import celery
from app import db
from app.models.car import Car
from app.services.parse_services import fetch_all_cars

# Configure logging
logging.basicConfig(
    filename="celery_sync.log",
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

@celery.task(name='tasks.sync.fetch_and_store_cars')
def fetch_and_store_cars():
    try:
        cars_data = fetch_all_cars()
        if not cars_data:
            msg = 'No car data fetched.'
            logging.info(msg)
            return msg

        for car_dict in cars_data:
            parse_id = car_dict.get('parse_id')
            if not parse_id:
                continue

            car = Car.query.filter_by(parse_id=parse_id).first()
            if not car:
                car = Car(parse_id=parse_id)

            car.make = car_dict.get('make')
            car.model = car_dict.get('model')
            car.year = car_dict.get('year')
            car.name = f"{car.make} {car.model}"
            car.created_at = car_dict.get('created_at')

            db.session.add(car)

        db.session.commit()

        msg = f"Successfully synced {len(cars_data)} cars."
        logging.info(msg)
        return msg

    except Exception as e:
        error_msg = f"Error syncing cars: {str(e)}"
        logging.error(error_msg)
        return error_msg
