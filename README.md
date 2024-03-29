[![hacs_badge](https://img.shields.io/badge/HACS-Default-41BDF5.svg?style=for-the-badge)](https://github.com/hacs/integration)
[![Validate with HACS](https://img.shields.io/github/actions/workflow/status/barleybobs/homeassistant-ecowater-softener/validate-hacs.yml?label=Validate%20with%20HACS&style=for-the-badge)](https://github.com/barleybobs/homeassistant-ecowater-softener/actions)
[![Validate with Hassfest](https://img.shields.io/github/actions/workflow/status/barleybobs/homeassistant-ecowater-softener/validate-with-hassfest.yml?label=Validate%20with%20Hassfest&style=for-the-badge)](https://github.com/barleybobs/homeassistant-ecowater-softener/actions)

# **V3.0.0 BREAKING CHANGES**
**In version 3.0.0 the original sensor is discontinued. There are now individual entities for each piece of data. These new sensor also update every 10 minutes compared to the old sensor which updated every 30 minutes.**

**Before installing version 3.0.0 remove the integration from the "Device and Services" menu. Then install version 3.0.0 and restart before finally setting up the integration again.**

# Ecowater water softeners integration for Home Assistant

`ecowater_softener` is a _custom component_ for [Home Assistant](https://www.home-assistant.io/). The integration allows you to pull data from your Ecowater water softener.

## Installation

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
- [@figorr](https://github.com/figorr) - Updated deprecated constants
- [@kylejohnson](https://github.com/kylejohnson) - Discovering and documenting the Ecowater API
- [@mattjgalloway](https://github.com/mattjgalloway) - Sorting manifest.json ordering
- [@Tazmanian79](https://github.com/Tazmanian79) - Updating state class from measurement to total

## License
[MIT](https://choosealicense.com/licenses/mit/)
