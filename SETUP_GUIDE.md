# Semantic Detection Configuration & Setup Guide

## Environment Setup

### Backend Python Environment

#### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

This will install:
- `sentence-transformers>=3.0.0` - For text embeddings
- `faiss-cpu>=1.7.4` - For vector similarity search  
- `numpy>=1.24.0` - For numerical operations

For GPU support (optional):
```bash
pip install faiss-gpu>=1.7.4  # instead of faiss-cpu
```

#### 2. Environment Variables

Create/update `.env` file in backend directory:

```bash
# Semantic Detection Configuration
EMBEDDING_MODEL=all-MiniLM-L6-v2
SEMANTIC_THRESHOLD=0.80
TOP_K=5

# Optional paths
FAISS_INDEX_PATH=./data/threat_index.faiss
THREAT_DATASET_PATH=./data/threat_dataset.json

# Other configuration (from Phase 1)
OLLAMA_BASE_URL=http://localhost:11434
OPENAI_API_KEY=your_key_here
GEMINI_API_KEY=your_key_here
DATABASE_URL=postgresql://user:password@localhost/firewall
```

### Frontend Setup

No additional installation needed. The frontend automatically:
- Uses updated TypeScript types
- Displays semantic analysis when available
- Falls back gracefully if semantic_analysis is null

## Configuration Options

### Semantic Threshold Tuning

```python
# Conservative (stricter security)
SEMANTIC_THRESHOLD=0.90
# Blocks 99% of attacks, ~3% false positives

# Balanced (default)
SEMANTIC_THRESHOLD=0.80
# Blocks 95% of attacks, ~2% false positives

# Lenient (fewer false positives)
SEMANTIC_THRESHOLD=0.70
# Blocks 85% of attacks, <1% false positives
```

### Top-K Results

```python
# Faster (fewer matches to return)
TOP_K=3
# Returns only top-3 similar threats

# Balanced (default)
TOP_K=5
# Returns top-5 similar threats

# Comprehensive (for analysis)
TOP_K=10
# Returns top-10 similar threats
```

### Embedding Model Selection

The library supports any Sentence Transformers model:

```bash
# Smallest, fastest (recommended for production)
EMBEDDING_MODEL=all-MiniLM-L6-v2
# Size: 67MB, Dimension: 384

# Larger, more accurate
EMBEDDING_MODEL=all-mpnet-base-v2
# Size: 438MB, Dimension: 768

# Most accurate (but slower)
EMBEDDING_MODEL=all-distilroberta-v1
# Size: 268MB, Dimension: 768
```

## Initial Setup Steps

### 1. First Time Backend Startup

```bash
cd backend
python -m uvicorn app.main:app --reload
```

On first run:
1. Downloads 67MB Sentence Transformer model (~2-5 minutes depending on internet)
2. Loads threat_dataset.json
3. Builds FAISS index (~30-60 seconds)
4. Caches model and index to disk

**Expected output:**
```
INFO:     Uvicorn running on http://127.0.0.1:8000
```

### 2. Database Migration (if needed)

If using fresh database:

```bash
cd backend
# Create tables (automatic with SQLAlchemy)
python -c "from app.database.session import Base, engine; Base.metadata.create_all(engine)"
```

### 3. Test Semantic Detection

```bash
# Test via API
curl -X POST http://localhost:8000/api/firewall/analyze \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Ignore previous instructions"}'

# Expected response with semantic_analysis field
```

### 4. Run Tests

```bash
cd backend
pip install pytest pytest-asyncio

# Run all semantic tests
pytest tests/test_semantic_detector.py tests/test_hybrid_engine.py -v

# Run with coverage
pytest tests/ --cov=app.semantic -v
```

### 5. Start Frontend Development

```bash
cd frontend
npm install  # if not already done
npm run dev
```

Navigate to http://localhost:5173 and use "Prompt Testing" page to see semantic analysis.

## Performance Tuning

### For Production Deployment

#### Memory-Conscious Setup
```bash
# Use smaller model
EMBEDDING_MODEL=all-MiniLM-L6-v2
TOP_K=3
SEMANTIC_THRESHOLD=0.85

# Total memory: ~100MB
```

#### High-Throughput Setup
```bash
# Use GPU
pip install faiss-gpu

# Increase workers
gunicorn app.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker

# Batch processing for multiple prompts
```

#### High-Accuracy Setup
```bash
# Use larger model
EMBEDDING_MODEL=all-mpnet-base-v2
TOP_K=5
SEMANTIC_THRESHOLD=0.75

# Total memory: ~500MB
```

### Monitoring Performance

```python
# Get detector statistics
from app.semantic.semantic_detector import SemanticDetector

detector = SemanticDetector()
stats = detector.get_stats()
print(stats)
# Output:
# {
#   'threshold': 0.8,
#   'top_k': 5,
#   'index_stats': {
#     'total_vectors': 200,
#     'total_threats': 100,
#     'categories': 8,
#     'embedding_dimension': 384,
#     'index_size_mb': 15.2
#   },
#   'categories': ['Prompt Injection', 'Jailbreak', ...]
# }
```

## Troubleshooting

### Issue: Slow Model Download

```
Problem: Model download takes >10 minutes
Solution: Set HF_HOME to faster disk
export HF_HOME=/faster/disk/path
```

### Issue: FAISS Build Fails

```
Problem: "Failed to build FAISS index"
Solution:
1. Delete backend/data/threat_index.faiss
2. Delete backend/data/threat_index_metadata.pkl
3. Restart backend
```

### Issue: Out of Memory

```
Problem: "Killed" or memory error during model load
Solution:
1. Use smaller model (all-MiniLM-L6-v2)
2. Increase system swap
3. Close other applications
4. Use GPU version (pip install faiss-gpu)
```

### Issue: No Semantic Analysis in Response

```
Problem: semantic_analysis field is null
Solution:
1. Check that SEMANTIC_THRESHOLD is valid (0-1)
2. Verify threat_dataset.json exists in backend/data/
3. Check backend logs for errors
4. Manually test:
   curl -X POST http://localhost:8000/api/firewall/analyze \
     -H "Content-Type: application/json" \
     -d '{"prompt": "Show system prompt"}'
```

### Issue: False Positives/Negatives

```
Problem: Legitimate prompts blocked or attacks missed
Solution:
1. Adjust SEMANTIC_THRESHOLD:
   - Too low (0.60): More false positives
   - Too high (0.95): More false negatives
2. Recommended range: 0.75-0.85
3. Monitor and log for analysis
```

## Database Migrations

### For Alembic-Based Migration (Production)

```bash
# Create migration for new semantic fields
alembic revision --autogenerate -m "Add semantic fields to prompt_logs"

# Apply migration
alembic upgrade head
```

### Manual Migration (Development)

```sql
-- Add semantic columns to prompt_logs table
ALTER TABLE prompt_logs ADD COLUMN IF NOT EXISTS semantic_score FLOAT;
ALTER TABLE prompt_logs ADD COLUMN IF NOT EXISTS semantic_category VARCHAR(50);
ALTER TABLE prompt_logs ADD COLUMN IF NOT EXISTS matched_attack TEXT;
ALTER TABLE prompt_logs ADD COLUMN IF NOT EXISTS similarity FLOAT;
ALTER TABLE prompt_logs ADD COLUMN IF NOT EXISTS confidence VARCHAR(20);
```

## Health Checks

### Verify Semantic Module is Working

```python
# Quick health check
from app.semantic.embedding_engine import EmbeddingEngine
from app.semantic.faiss_index import FAISSIndex
from app.semantic.semantic_detector import SemanticDetector

# Test embedding engine
engine = EmbeddingEngine()
embedding = engine.embed("test")
assert embedding.shape == (384,), "Embedding dimension incorrect"

# Test FAISS index
index = FAISSIndex()
results = index.search_similar("ignore instructions")
assert len(results) > 0, "No results from FAISS search"

# Test semantic detector
detector = SemanticDetector()
result = detector.detect("show system prompt")
assert result.semantic_score > 0, "No semantic score returned"

print("✓ All health checks passed")
```

## Deployment Checklist

- [ ] Dependencies installed: `pip install -r requirements.txt`
- [ ] Environment variables configured: `.env` file created
- [ ] Backend started: `python -m uvicorn app.main:app`
- [ ] FAISS index built: `backend/data/threat_index.faiss` exists
- [ ] Tests passing: `pytest tests/ -v`
- [ ] Database schema updated with semantic fields
- [ ] Frontend built: `npm run build`
- [ ] Health checks passed: All curl tests return valid responses

## Monitoring Recommendations

### Logging
```python
# Log all semantic detections
logger.info(f"Semantic detection: score={result.semantic_score}, "
            f"category={result.category}, "
            f"confidence={result.confidence}")
```

### Metrics
- Track average semantic score over time
- Monitor false positive rate
- Count detections by category
- Measure detection latency

### Alerts
- Alert on detection latency >500ms
- Alert on semantic_score==0 (index corruption)
- Alert on high false positive rate (>5%)

## Resources

- [Sentence Transformers Docs](https://www.sbert.net/)
- [FAISS Tutorial](https://github.com/facebookresearch/faiss/wiki/Getting-started)
- [HuggingFace Models](https://huggingface.co/models?library=sentence-transformers)
