from CarPlateParking_Infra import UserInputHandler, ImageHandler, LicensePlateHandler, RedisDB

if __name__ == "__main__":
    user_input = UserInputHandler()
    while user_input.is_valid():
        image = ImageHandler(user_input.get_user_input(), user_input.get_input_type())
        txt = image.extract_txt_from_image()
        license_plate = LicensePlateHandler(txt)
        if license_plate.is_valid():
            redis_db = RedisDB()
            if redis_db.check_in_db(license_plate.get_license_plate(), user_input.get_input_time()) is None:
                access = license_plate.check_parking_access()
                redis_db.save_to_db(license_plate.get_license_plate(), license_plate.get_car_type(),
                                    user_input.get_input_time(), access)

        user_input = UserInputHandler()

    print("Goodbye")
