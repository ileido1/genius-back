import math
from django.http import JsonResponse
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from api.serializers import MyTokenObtainPairSerializer, RegisterSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework import generics
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth.models import User
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from .models import CsvData
import pandas as pd
import os
import requests
from django.conf import settings
from django.http import JsonResponse
import nltk
from collections import Counter
import re
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk import FreqDist
import emoji
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.decorators import api_view, permission_classes


nltk.download('stopwords')

API_URL_SENTIMENT = "https://api-inference.huggingface.co/models/finiteautomata/beto-sentiment-analysis"
API_URL_EMOTION = "https://api-inference.huggingface.co/models/finiteautomata/beto-emotion-analysis"
HEADERS = {"Authorization": "Bearer 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"}
# @permission_classes([IsAuthenticated])
class ProcessDataView(APIView):
    ITEMS_PER_PAGE = 10
    def post(self, request, *args, **kwargs):
        try:
           # Obtener el número de página del cuerpo de la solicitud
           
            page = int(request.data.get('page', 1))

            csv_file_path = os.path.join(settings.BASE_DIR, 'api', 'DataRedesSociales.csv')
            df = pd.read_csv(csv_file_path)

            analyzed_results = []

            # Otras estadísticas
            total_likes = 0
            total_comments = 0
            total_shares = 0
            sentiment_stats = Counter()
            emotion_stats = Counter()
            words_stats = Counter()
            interactions = Counter()
            emojis_stats = Counter()
            hashtags_stats = Counter()
            mentions_stats = Counter()

            # Obtener el número total de registros
            total_records = df.shape[0]

            # Obtener el número total de páginas (considerando ITEMS_PER_PAGE)
            total_pages = math.ceil(total_records / self.ITEMS_PER_PAGE)

            # Calcular el índice de inicio y fin para la paginación
            start_index = (page - 1) * self.ITEMS_PER_PAGE
            end_index = min(page * self.ITEMS_PER_PAGE, total_records)

            # Filtrar el DataFrame para obtener los registros de la página actual
            paginated_df = df.iloc[start_index:end_index]

            for index, row in paginated_df.iterrows():
                csv_data = CsvData.objects.create(
                    text=row['text'],
                    likes=row['likes'],
                    comments=row['comments'],
                    shares=row['shares'],
                    reactions_count=row['reactions_count']
                )

                total_likes += csv_data.likes
                total_comments += csv_data.comments
                total_shares += csv_data.shares

                sentiment_result = self.query_api(API_URL_SENTIMENT, csv_data.text)
                emotion_result = self.query_api(API_URL_EMOTION, csv_data.text)
                

                # Actualiza estadísticas de sentimiento y emoción
                sentiment_stats.update([sentiment_result[0][0]['label']])
                emotion_stats.update([emotion_result[0][0]['label']])

                # Procesa las palabras más usadas
                words = re.findall(r'\b\w+\b', csv_data.text.lower())
                filtered_words = [word for word in words if word not in stopwords.words('spanish')]
                words_stats.update(filtered_words)

               

                # Procesa hashtags y menciones
                hashtags = re.findall(r'#\w+', csv_data.text)
                mentions = re.findall(r'@\w+', csv_data.text)
                hashtags_stats.update(hashtags)
                mentions_stats.update(mentions)

                # Actualiza estadísticas de interacciones
                interactions[index] = csv_data.likes + csv_data.comments + csv_data.shares

                if sentiment_result and emotion_result:
                    csv_data.sentiment_label = sentiment_result[0][0]['label']
                    csv_data.sentiment_score = sentiment_result[0][0]['score']
                    csv_data.emotion_label = emotion_result[0][0]['label']
                    csv_data.emotion_score = emotion_result[0][0]['score']
                    csv_data.save()

                    analyzed_results.append({
                        'text': csv_data.text,
                        'sentiment_label': csv_data.sentiment_label,
                        'sentiment_score': csv_data.sentiment_score,
                        'emotion_label': csv_data.emotion_label,
                        'emotion_score': csv_data.emotion_score,
                    })
                else:
                    print("Error: Invalid structure in sentiment_result or emotion_result")
                results = {
                'total_likes': total_likes,
                'total_comments': total_comments,
                'total_shares': total_shares,
                'sentiment_stats': dict(sentiment_stats),
                'emotion_stats': dict(emotion_stats),
                'words_stats': dict(words_stats),
                'hashtags_stats': dict(hashtags_stats),
                'mentions_stats': dict(mentions_stats),
            }
        except Exception as e:
            import traceback
            traceback.print_exc() 
            print(f"Error: {e}")
            return JsonResponse({'error': str(e)}, status=500)

        return Response({'message': 'Data processing completed!', 'results': analyzed_results, 'info': results})

    def query_api(self, api_url, text):
        payload = {
            "inputs": text,
            "options": {"wait_for_model": True}
        }
        try:
            response = requests.post(api_url, headers=HEADERS, json=payload)
            response_data = response.json()

            if 'error' in response_data and 'Rate limit reached' in response_data['error']:
                raise RateLimitError(response_data['error'])

            return response_data

        except RateLimitError as e:
            print(f"Rate limit error: {e}")
            return {'error': 'Rate limit reached. Please try again later or subscribe to a plan.'}

        except Exception as e:
            # Log and handle other errors
            print(f"Error: {e}")
            return {'error': 'An unexpected error occurred. Please try again later.'}

class RateLimitError(Exception):
    pass
#Login User
class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer

#Register User
class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer

class LogoutView(APIView):
    def delete(self, request):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({'message': 'Successfully logged out.'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': 'Invalid refresh token.'}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def getRoutes(request):
    routes = [
        '/api/signin/',
        '/api/register/',
        '/api/token/refresh/',
        '/api/logout',
        'api/process-csv/'
    ]
    return Response(routes)
