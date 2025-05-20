# NLP Pipeline API

A robust and scalable Natural Language Processing (NLP) pipeline built with FastAPI, providing various NLP services including text classification, entity extraction, summarization, and sentiment analysis.

## Features

- **NLP Services**
  - Text Classification
  - Entity Extraction
  - Text Summarization
  - Sentiment Analysis

- **Advanced Features**
  - Batch Processing
  - Webhook Notifications
  - Caching System
  - Rate Limiting
  - Monitoring with Prometheus
  - RAG (Retrieval-Augmented Generation) Support

## Prerequisites

- Python 3.8+
- PostgreSQL
- Redis
- UltraSafe API Key

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd nlp_pipeline
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Configuration

The application uses environment variables for configuration. You can set them in a `.env` file or directly in your environment. Key configurations include:

- Database settings (PostgreSQL)
- Redis connection details
- UltraSafe API credentials
- Security settings
- Cache and rate limiting configurations

## Running the Application

1. Start the FastAPI server:
```bash
python run.py
```

The API will be available at `http://localhost:8000`

2. Access the API documentation:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## API Endpoints

### NLP Endpoints
- `POST /api/v1/nlp/classify` - Text classification
- `POST /api/v1/nlp/extract-entities` - Entity extraction
- `POST /api/v1/nlp/summarize` - Text summarization
- `POST /api/v1/nlp/analyze-sentiment` - Sentiment analysis
- `GET /api/v1/nlp/task/{task_id}` - Get task status

### Batch Processing
- `POST /api/v1/batch/submit` - Submit batch job
- `GET /api/v1/batch/{job_id}/status` - Get batch job status
- `GET /api/v1/batch/{job_id}/results` - Get batch job results
- `DELETE /api/v1/batch/{job_id}` - Cancel batch job

### Webhooks
- `POST /api/v1/webhooks/` - Register webhook
- `GET /api/v1/webhooks/` - List webhooks
- `DELETE /api/v1/webhooks/{webhook_id}` - Delete webhook
- `POST /api/v1/webhooks/{webhook_id}/test` - Test webhook

## Development

### Project Structure
```
nlp_pipeline/
├── app/
│   ├── api/
│   │   └── endpoints/
│   ├── core/
│   ├── models/
│   ├── services/
│   └── tests/
├── docs/
├── scripts/
└── deployment/
```

### Running Tests
```bash
pytest
```

## Monitoring

The application includes Prometheus metrics at `/metrics` endpoint. You can use these metrics with Grafana for visualization.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support, please open an issue in the repository or contact the maintainers.
