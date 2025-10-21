from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
from .models import StringAnalysis
from .serializers import StringAnalysisSerializer
from .utils import analyze_string
import hashlib



from django.http import JsonResponse

def home(request):
    return JsonResponse({"message": "String Analyzer API is running 🚀"})

# Natural Language Parser Helper
def parse_natural_query(query: str):
    q = query.lower()
    parsed = {}

    if "palindromic" in q or "palindrome" in q:
        parsed["is_palindrome"] = True

    if "single word" in q or "one word" in q:
        parsed["word_count"] = 1

    import re
    match = re.search(r"longer than (\d+)", q)
    if match:
        parsed["min_length"] = int(match.group(1)) + 1

    if "containing the letter" in q:
        match = re.search(r"letter (\w)", q)
        if match:
            parsed["contains_character"] = match.group(1)

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
    value = string_value
    id_ = hashlib.sha256(value.encode('utf-8')).hexdigest()
    try:
        obj = StringAnalysis.objects.get(id=id_)
    except StringAnalysis.DoesNotExist:
        return Response({"error": "String not found"}, status=404)
    serializer = StringAnalysisSerializer(obj)
    return Response(serializer.data)


@api_view(['GET'])
def list_strings(request):
    qs = StringAnalysis.objects.all()
    filters_applied = {}

    is_palindrome = request.GET.get("is_palindrome")
    min_length = request.GET.get("min_length")
    max_length = request.GET.get("max_length")
    word_count = request.GET.get("word_count")
    contains_character = request.GET.get("contains_character")

    # Filters
    if is_palindrome is not None:
        val = is_palindrome.lower() == "true"
        qs = [x for x in qs if x.properties["is_palindrome"] == val]
        filters_applied["is_palindrome"] = val

    if min_length:
        qs = [x for x in qs if x.properties["length"] >= int(min_length)]
        filters_applied["min_length"] = int(min_length)

    if max_length:
        qs = [x for x in qs if x.properties["length"] <= int(max_length)]
        filters_applied["max_length"] = int(max_length)

    if word_count:
        qs = [x for x in qs if x.properties["word_count"] == int(word_count)]
        filters_applied["word_count"] = int(word_count)

    if contains_character:
        if len(contains_character) != 1:
            return Response({"error": "contains_character must be single character"}, status=400)
        qs = [x for x in qs if contains_character in x.value]
        filters_applied["contains_character"] = contains_character

    serializer = StringAnalysisSerializer(qs, many=True)
    return Response({
        "data": serializer.data,
        "count": len(serializer.data),
        "filters_applied": filters_applied
    })


@api_view(['GET'])
def filter_natural(request):
    query = request.GET.get("query")
    if not query:
        return Response({"error": "Missing query parameter"}, status=400)
    try:
        parsed = parse_natural_query(query)
    except ValueError as e:
        return Response({"error": str(e)}, status=400)

    # Reuse list_strings logic manually
    qs = StringAnalysis.objects.all()
    if parsed.get("is_palindrome"):
        qs = [x for x in qs if x.properties["is_palindrome"]]
    if parsed.get("word_count"):
        qs = [x for x in qs if x.properties["word_count"] == parsed["word_count"]]
    if parsed.get("min_length"):
        qs = [x for x in qs if x.properties["length"] >= parsed["min_length"]]
    if parsed.get("contains_character"):
        qs = [x for x in qs if parsed["contains_character"] in x.value]

    serializer = StringAnalysisSerializer(qs, many=True)
    return Response({
        "data": serializer.data,
        "count": len(serializer.data),
        "interpreted_query": {
            "original": query,
            "parsed_filters": parsed
        }
    })


@api_view(['DELETE'])
def delete_string(request, string_value):
    id_ = hashlib.sha256(string_value.encode('utf-8')).hexdigest()
    deleted, _ = StringAnalysis.objects.filter(id=id_).delete()
    if deleted == 0:
        return Response({"error": "String not found"}, status=404)
    return Response(status=204)
