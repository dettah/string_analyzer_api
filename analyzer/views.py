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
            parsed["contains_character"] = match.group(1).lower()

    if "first vowel" in q:
        parsed["contains_character"] = "a"

    if not parsed:
        raise ValueError("Unable to parse query")
    return parsed

@api_view(['POST'])
def create_string(request):
    value = request.data.get("value")
    if value is None:
        return Response({"error": '"value" field is required'}, status=400)
    if not isinstance(value, str):
        return Response({"error": '"value" must be a string'}, status=422)

    props = analyze_string(value)
    id_ = props["sha256_hash"]

    if StringAnalysis.objects.filter(id=id_).exists():
        return Response({"error": "String already exists"}, status=409)

    obj = StringAnalysis.objects.create(
        id=id_,
        value=value,
        properties=props
    )
    serializer = StringAnalysisSerializer(obj)
    return Response(serializer.data, status=201)

@api_view(['GET'])
def get_string(request, string_value):
    string_value = unquote(string_value)
    id_ = hashlib.sha256(string_value.encode('utf-8')).hexdigest()
    try:
        obj = StringAnalysis.objects.get(id=id_)
    except StringAnalysis.DoesNotExist:
        return Response({"error": "String not found"}, status=404)
    serializer = StringAnalysisSerializer(obj)
    return Response(serializer.data)

@api_view(['DELETE'])
def delete_string(request, string_value):
    string_value = unquote(string_value)
    id_ = hashlib.sha256(string_value.encode('utf-8')).hexdigest()
    deleted, _ = StringAnalysis.objects.filter(id=id_).delete()
    if deleted == 0:
        return Response({"error": "String not found"}, status=404)
    return Response(status=204)

@api_view(['GET', 'POST'])
def string_collection(request):
    if request.method == 'POST':
        value = request.data.get("value")
        if value is None:
            return Response({"error": '"value" field is required'}, status=400)
        if not isinstance(value, str):
            return Response({"error": '"value" must be a string'}, status=422)

        props = analyze_string(value)
        id_ = props["sha256_hash"]

        if StringAnalysis.objects.filter(id=id_).exists():
            return Response({"error": "String already exists"}, status=409)

        obj = StringAnalysis.objects.create(
            id=id_,
            value=value,
            properties=props
        )
        serializer = StringAnalysisSerializer(obj)
        return Response(serializer.data, status=201)
    
    qs = StringAnalysis.objects.all()
    filters_applied = {}

    is_palindrome = request.GET.get("is_palindrome")
    if is_palindrome is not None:
        lowered = is_palindrome.lower()
        if lowered not in ["true", "false"]:
            return Response({"error": "is_palindrome must be 'true' or 'false'"}, status=400)
        val = lowered == "true"
        qs = qs.filter(properties__is_palindrome=val)
        filters_applied["is_palindrome"] = val

    min_length = request.GET.get("min_length")
    if min_length is not None:
        try:
            min_l = int(min_length)
            qs = qs.filter(properties__length__gte=min_l)
            filters_applied["min_length"] = min_l
        except ValueError:
            return Response({"error": "min_length must be an integer"}, status=400)

    max_length = request.GET.get("max_length")
    if max_length is not None:
        try:
            max_l = int(max_length)
            qs = qs.filter(properties__length__lte=max_l)
            filters_applied["max_length"] = max_l
        except ValueError:
            return Response({"error": "max_length must be an integer"}, status=400)

    word_count = request.GET.get("word_count")
    if word_count is not None:
        try:
            wc = int(word_count)
            qs = qs.filter(properties__word_count=wc)
            filters_applied["word_count"] = wc
        except ValueError:
            return Response({"error": "word_count must be an integer"}, status=400)

    contains_character = request.GET.get("contains_character")
    if contains_character is not None:
        if len(contains_character) != 1:
            return Response({"error": "contains_character must be single character"}, status=400)
        qs = qs.filter(value__icontains=contains_character)
        filters_applied["contains_character"] = contains_character

    serializer = StringAnalysisSerializer(qs, many=True)
    return Response({
        "data": serializer.data,
        "count": qs.count(),
        "filters_applied": filters_applied
    })

@api_view(['GET', 'DELETE'])
def string_detail(request, string_value):
    string_value = unquote(string_value)
    if request.method == 'GET':
        # FIXED: COPY GET LOGIC HERE (NO RECURSION!)
        id_ = hashlib.sha256(string_value.encode('utf-8')).hexdigest()
        try:
            obj = StringAnalysis.objects.get(id=id_)
        except StringAnalysis.DoesNotExist:
            return Response({"error": "String not found"}, status=404)
        serializer = StringAnalysisSerializer(obj)
        return Response(serializer.data)
    elif request.method == 'DELETE':
        # FIXED: COPY DELETE LOGIC HERE (NO RECURSION!)
        id_ = hashlib.sha256(string_value.encode('utf-8')).hexdigest()
        deleted, _ = StringAnalysis.objects.filter(id=id_).delete()
        if deleted == 0:
            return Response({"error": "String not found"}, status=404)
        return Response(status=204)

@api_view(['GET'])
def filter_natural(request):
    query = request.GET.get("query")
    if not query:
        return Response({"error": "Missing query parameter"}, status=400)
    try:
        parsed = parse_natural_query(query)
    except ValueError as e:
        return Response({"error": str(e)}, status=400)

    qs = StringAnalysis.objects.all()

    if parsed.get("is_palindrome"):
        qs = qs.filter(properties__is_palindrome=True)

    if "word_count" in parsed:
        qs = qs.filter(properties__word_count=parsed["word_count"])

    if "min_length" in parsed:
        qs = qs.filter(properties__length__gte=parsed["min_length"])

    if "contains_character" in parsed:
        char = parsed["contains_character"]
        qs = qs.filter(value__icontains=char)

    serializer = StringAnalysisSerializer(qs, many=True)
    return Response({
        "data": serializer.data,
        "count": qs.count(),
        "interpreted_query": {
            "original": query,
            "parsed_filters": parsed
        }
    })
