from django.http import JsonResponse
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
from urllib.parse import unquote
from .models import StringAnalysis
from .serializers import StringAnalysisSerializer
from .utils import analyze_string
import hashlib
import re

def home(request):
    return JsonResponse({"message": "String Analyzer API is running 🚀"})

@api_view(['GET', 'POST'])
def strings(request):
    """GET /strings/ (list + filters) + POST /strings/ (create)"""
    if request.method == 'POST':
        # Early validation to prevent crashes
        value = request.data.get('value')
        if value is None:
            return Response({"error": '"value" field is required'}, status=status.HTTP_400_BAD_REQUEST)
        if not isinstance(value, str):
            return Response({"error": '"value" must be a string'}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        if not value.strip():
            return Response({"error": '"value" cannot be empty'}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        
        try:
            props = analyze_string(value)
            id_ = props["sha256_hash"]
            
            if StringAnalysis.objects.filter(id=id_).exists():
                return Response({"error": "String already exists"}, status=status.HTTP_409_CONFLICT)
            
            obj = StringAnalysis.objects.create(id=id_, value=value, properties=props)
            serializer = StringAnalysisSerializer(obj)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as exc:
            return Response({"error": f"Internal error: {str(exc)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    # GET logic (list + filters)
    qs = StringAnalysis.objects.all()
    filters_applied = {}

    # is_palindrome
    is_palindrome = request.GET.get('is_palindrome')
    if is_palindrome is not None:
        try:
            val = str(is_palindrome).lower() == 'true'
            qs = qs.filter(properties__is_palindrome=val)
            filters_applied['is_palindrome'] = val
        except:
            return Response({"error": "is_palindrome must be 'true' or 'false'"}, status=status.HTTP_400_BAD_REQUEST)

    # min_length
    min_length = request.GET.get('min_length')
    if min_length is not None:
        try:
            qs = qs.filter(properties__length__gte=int(min_length))
            filters_applied['min_length'] = int(min_length)
        except ValueError:
            return Response({"error": "min_length must be an integer"}, status=status.HTTP_400_BAD_REQUEST)

    # max_length
    max_length = request.GET.get('max_length')
    if max_length is not None:
        try:
            qs = qs.filter(properties__length__lte=int(max_length))
            filters_applied['max_length'] = int(max_length)
        except ValueError:
            return Response({"error": "max_length must be an integer"}, status=status.HTTP_400_BAD_REQUEST)

    # word_count
    word_count = request.GET.get('word_count')
    if word_count is not None:
        try:
            qs = qs.filter(properties__word_count=int(word_count))
            filters_applied['word_count'] = int(word_count)
        except ValueError:
            return Response({"error": "word_count must be an integer"}, status=status.HTTP_400_BAD_REQUEST)

    # contains_character
    contains_character = request.GET.get('contains_character')
    if contains_character is not None:
        if len(str(contains_character)) != 1:
            return Response({"error": "contains_character must be single character"}, status=status.HTTP_400_BAD_REQUEST)
        qs = qs.filter(value__icontains=str(contains_character))
        filters_applied['contains_character'] = str(contains_character)

    try:
        serializer = StringAnalysisSerializer(qs, many=True)
        return Response({
            "data": serializer.data,
            "count": qs.count(),
            "filters_applied": filters_applied
        })
    except Exception as exc:
        return Response({"error": f"Internal error: {str(exc)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET', 'DELETE'])
def string_detail(request, string_value):
    """GET/DELETE /strings/{value}/"""
    try:
        string_value = unquote(string_value)
        id_ = hashlib.sha256(string_value.encode('utf-8')).hexdigest()
        
        if request.method == 'GET':
            obj = StringAnalysis.objects.get(id=id_)
            serializer = StringAnalysisSerializer(obj)
            return Response(serializer.data)
        
        if request.method == 'DELETE':
            deleted_count, _ = StringAnalysis.objects.filter(id=id_).delete()
            if deleted_count == 0:
                return Response({"error": "String not found"}, status=status.HTTP_404_NOT_FOUND)
            return Response(status=status.HTTP_204_NO_CONTENT)
    except StringAnalysis.DoesNotExist:
        return Response({"error": "String not found"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as exc:
        return Response({"error": f"Internal error: {str(exc)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

def parse_natural_query(query: str):
    q = query.lower()
    parsed = {}
    if "palindromic" in q or "palindrome" in q:
        parsed["is_palindrome"] = True
    if "single word" in q or "one word" in q:
        parsed["word_count"] = 1
    match = re.search(r"longer than (\d+)", q)
    if match:
        parsed["min_length"] = int(match.group(1)) + 1
    if "containing the letter" in q:
        match = re.search(r"letter (\w)", q)
        if match:
            parsed["contains_character"] = match.group(1)
    if "first vowel" in q:
        parsed["contains_character"] = "a"
    if "letter z" in q:
        parsed["contains_character"] = "z"
    if not parsed:
        raise ValueError("Unable to parse natural language query")
    return parsed

@api_view(['GET'])
def filter_natural(request):
    """GET /strings/filter-by-natural-language/"""
    query = request.GET.get("query")
    if not query:
        return Response({"error": "Missing query parameter"}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        parsed = parse_natural_query(query)
        qs = StringAnalysis.objects.all()
        
        if parsed.get("is_palindrome"):
            qs = qs.filter(properties__is_palindrome=True)
        if "word_count" in parsed:
            qs = qs.filter(properties__word_count=parsed["word_count"])
        if "min_length" in parsed:
            qs = qs.filter(properties__length__gte=parsed["min_length"])
        if "contains_character" in parsed:
            qs = qs.filter(value__icontains=parsed["contains_character"])
        
        serializer = StringAnalysisSerializer(qs, many=True)
        return Response({
            "data": serializer.data,
            "count": qs.count(),
            "interpreted_query": {"original": query, "parsed_filters": parsed}
        })
    except ValueError as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as exc:
        return Response({"error": f"Internal error: {str(exc)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)