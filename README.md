[![hacs_badge](https://img.shields.io/badge/HACS-Default-41BDF5.svg?style=for-the-badge)](https://github.com/hacs/integration)
[![Validate with HACS](https://img.shields.io/github/actions/workflow/status/barleybobs/homeassistant-ecowater-softener/validate-hacs.yml?label=Validate%20with%20HACS&style=for-the-badge)](https://github.com/barleybobs/homeassistant-ecowater-softener/actions)
[![Validate with Hassfest](https://img.shields.io/github/actions/workflow/status/barleybobs/homeassistant-ecowater-softener/validate-with-hassfest.yml?label=Validate%20with%20Hassfest&style=for-the-badge)](https://github.com/barleybobs/homeassistant-ecowater-softener/actions)

# **V3.0.0 BREAKING CHANGES**
**In version 3.0.0 the original sensor is discontinued. There are now individual entities for each piece of data. These new sensor also update every 10 minutes compared to the old sensor which updated every 30 minutes.**

**Note: Sept. 2024. Due to new limit of the api calls set by Ecowater, in order to avoid the blocking of the integration and the mobile app, that will show status as "Online" but it won't update the data until you powercycle the Ecowater Softener, the time between scans was set again to 30 minutes.**

**Before installing version 3.0.0 remove the integration from the "Device and Services" menu. Then install version 3.0.0 and restart before finally setting up the integration again.**

# Ecowater water softeners integration for Home Assistant

`ecowater_softener` is a _custom component_ for [Home Assistant](https://www.home-assistant.io/). The integration allows you to pull data from your Ecowater water softener.

## Current version: v3.4.3

## Changelog
Version 3.4.3
- Added translation not only to the setup process, the name of the sensor can also be translated using the translation_key code.
- Updated translation json files to be able to translate the name sensors.
- Updated the strings.json file.

Version 3.4.2
- Added "Last Update" sensor to show date and time from the last connection to API with "Online" Status.
- Added Spanish Translation.
- Some minor changes. OUT OF SALT ON ... now gives the data d/m/Y instead Y/m/d when date format at setup is dd/mm/yyyy
- Update Readme file to show the current version and changelog.
- Set default time between scans to 30 minutes, in order to avoid the integration and the mobile were blocked due the limit of api calls.

Version 3.4.1
- Fixed invalid regex warning - Updated regex by @figorr

Version 3.4.0
- Updated to using await async_forward_entry_setups - by @figorr
- Grammar fixes - by @heytcass

## Installation

#### Home Assistant helpers

You need to manually create a couple of helpers in Home Assistant to help the integration to manage the ability to edit the time scans between updates. By default is set to 30 minutes but you can increase or decrease it according to your needs. You can create them using configuration.yaml or using the UI.

1. Create an input_number to be able to edit this update interval.
   
   ```
   input_number:
     ecowater_update_interval:
      name: "Update Interval for Ecowater"
      min: 1
      max: 120
      step: 1
      unit_of_measurement: "minutes"
      icon: "mdi:timer"
      initial: 30  # Default value is 30 minutes
2. Create an input_button to save the changes once you have edited the update interval.

   ```
   input_button:
     ecowater_save_interval:
      name: "Save Update Interval for Ecowater"
      icon: "mdi:content-save"
#### HACS
1. Go to HACS -> Integrations -> Click +
1. Search for "Ecowater Softener" and add it to HACS
1. Restart Home Assistant
1. Go to Settings -> Devices & Services -> Integrations -> Click +
1. Search for "Ecowater Softener" and follow the set up instructions

#### Manually
Copy the `custom_components/ecowater_softener` folder into the config folder.

## Configuration
To add an Ecowater water softener, go to Configuration > Integrations in the UI. Then click the + button and from the list of integrations select Ecowater Softener. You should then see a dialog like the one below.

![Ecowater custom component setup dialog](images/setup.png)

You then need to enter the information you use to login on [https://wifi.ecowater.com/Site/Login](https://wifi.ecowater.com/Site/Login). (Serial Number = DSN)

Then you will need to select the date format that your Ecowater device uses. You can check this under the `Out of Salt Date` and `Last Recharge` at [https://wifi.ecowater.com/Site/Login](https://wifi.ecowater.com/Site/Login).

This will then create an device name "Ecowater SERIAL_NUMBER". 

![Device](images/integration.png)

This device will then have the entities show below.

![Entities](images/sensors.png)

## Credits

- [@ThePrincelle](https://github.com/ThePrincelle) - French Translations
- [@Quotic](https://github.com/Quotic) - German Translations
- [@figorr](https://github.com/figorr) - Updated deprecated constants & Updated to using `await async_forward_entry_setups` & Updated regex
- [@kylejohnson](https://github.com/kylejohnson) - Discovering and documenting the Ecowater API
- [@mattjgalloway](https://github.com/mattjgalloway) - Sorting manifest.json ordering
- [@Tazmanian79](https://github.com/Tazmanian79) - Updating state class from measurement to total
- [@heytcass](https://github.com/heytcass) - Grammar fixes

## License
[MIT](https://choosealicense.com/licenses/mit/)
