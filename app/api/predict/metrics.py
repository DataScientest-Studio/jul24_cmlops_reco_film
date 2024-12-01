from prometheus_client import Counter, Histogram, Info, Gauge

# Compteur pour le nombre total de prédictions
PREDICTION_REQUESTS = Counter(
    'prediction_requests_total',
    'Nombre total de requêtes de prédiction'
)

# Histogramme pour mesurer le temps de réponse
PREDICTION_LATENCY = Histogram(
    'prediction_latency_seconds',
    'Temps de traitement des prédictions',
    buckets=[0.1, 0.5, 1.0, 2.0, 5.0]
)

# Information sur le modèle
MODEL_INFO = Info('model_info', 'Informations sur le modèle de prédiction')

# Ajout du compteur pour les rechargements de modèle
MODEL_RELOAD_COUNTER = Counter(
    "model_reload_total", "Nombre total de rechargements du modèle"
)

# Nouvelles métriques
API_REQUESTS_TOTAL = Counter(
    'api_requests_total',
    'Nombre total de requêtes à l\'API',
    ['method', 'endpoint', 'status_code']
)

ACTIVE_REQUESTS = Gauge(
    'active_requests',
    'Nombre de requêtes actuellement en cours de traitement'
)
