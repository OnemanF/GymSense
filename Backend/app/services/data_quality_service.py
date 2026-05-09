class DataQualityService:
    MIN_TEMPERATURE = -10
    MAX_TEMPERATURE = 60

    MIN_HUMIDITY = 0
    MAX_HUMIDITY = 100

    MIN_PRESSURE = 800
    MAX_PRESSURE = 1100

    @staticmethod
    def is_valid_reading(reading) -> bool:
        if reading is None:
                return False

        if reading.temperature is None or reading.humidity is None or reading.pressure is None:
            return False

        if not DataQualityService.MIN_TEMPERATURE <= reading.temperature <= DataQualityService.MAX_TEMPERATURE:
            return False

        if not DataQualityService.MIN_HUMIDITY <= reading.humidity <= DataQualityService.MAX_HUMIDITY:
            return False

        if not DataQualityService.MIN_PRESSURE <= reading.pressure <= DataQualityService.MAX_PRESSURE:
            return False

        return True

