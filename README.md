# Gymsense

Gymsense is an IoT and AI-based gym environment monitoring prototype.  
The system collects indoor climate data from an ESP32 with sensors, stores the measurements in a PostgreSQL database, visualizes the data in a React dashboard, and uses a local LLM through Ollama to generate gym environment insights.

## Project purpose

The project is designed to help monitor whether a gym environment is comfortable for training.  
It focuses on temperature, humidity, pressure and relative light level. The AI part provides a short assessment and recommendation based on sensor data and curated gym climate guidelines.

## Features

- ESP32 sensor device
- BME280 temperature, humidity and pressure sensor
- LDR analog light sensor
- FastAPI backend with REST API
- PostgreSQL database on Render
- React frontend dashboard
- Historical charts for sensor readings
- AI insight generation using Ollama
- RAG-based guideline context
- LangChain agent with tools
- MCP server for controlled tool access
- Promptfoo prompt evaluation
- Unit tests with pytest
- Backend data validation to reject invalid sensor readings

## Tech stack

### IoT
- ESP32 / FireBeetle 2 ESP32-E
- PlatformIO
- Arduino framework
- BME280 via I2C
- LDR via ADC analog input
- HTTP POST with JSON

### Backend
- Python
- FastAPI
- SQLModel
- PostgreSQL
- Render database
- Uvicorn

### Frontend
- React
- Vite
- Recharts
- CSS

### AI
- Ollama
- phi3:mini
- LangChain
- RAG
- MCP
- Promptfoo
- pytest

## Architecture

```text
ESP32 + Sensors
      |
      | HTTP POST JSON
      v
FastAPI Backend
      |
      v
PostgreSQL Database
      |
      v
React Dashboard
      |
      v
AI Insights using Ollama + LangChain + RAG + MCP