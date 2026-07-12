"""ML integration — model loading, persistence, and prediction service.

This package connects the trained LightGBM model to the production valuation pipeline.
The model is loaded lazily from the model_registry table or a local models directory.
If no model is available, the API falls back to the statistical valuation engine.
"""
