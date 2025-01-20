from django.shortcuts import render
from django.db.models import Sum
from .models import AnnouncedPuResults, AnnouncedLgaResults, PollingUnit, Lga

def index(request):
    return render(request, "index.html")

def question_1(request):
    results = []
    if request.method == "POST":
        polling_unit_id = request.POST.get("polling_unit_id")
        results = AnnouncedPuResults.objects.filter(polling_unit_uniqueid=polling_unit_id).values(
            "party_abbreviation", "party_score"
        )
    return render(request, "question_1.html", {"results": results})

def question_2(request):
    party_scores = {}
    if request.method == "POST":
        lga_name = request.POST.get("lga_name")
        
        # Get the LGA ID from the LGA name
        lga_id = Lga.objects.filter(lga_name=lga_name).values_list("lga_id", flat=True).first()
        
        #pass to the polling unit to get the unique id
        # for each polling unnit unique id, get each party score and sum it up
        # then return a total score for each party
        polling_units = list(PollingUnit.objects.filter(lga_id=lga_id).values_list("uniqueid", flat=True))
        print(polling_units)

        party_scores = AnnouncedPuResults.objects.filter(polling_unit_uniqueid__in=polling_units).values(
            "party_abbreviation"
        ).annotate(total_score=Sum("party_score"))
        
        # Ensure all rows are being considered
        party_scores = list(party_scores)
        print(party_scores)
        
    return render(request, "question_2.html", {"party_scores": party_scores, "lga_name": lga_name})

def question_3(request):
    results = []
    if request.method == "POST":
        lga_name = request.POST.get("lga_name")
        polling_units = PollingUnit.objects.filter(lga__lga_name=lga_name)
        for unit in polling_units:
            unit_results = AnnouncedPuResults.objects.filter(polling_unit_uniqueid=unit.uniqueid).values(
                "party_abbreviation", "party_score"
            )
            results.append({"polling_unit": unit.polling_unit_name, "results": list(unit_results)})
    return render(request, "question_3.html", {"results": results})


def handle_questions(request):
    result = ""
    if request.method == "POST":
        question = request.POST.get("question")
        
        if question == "1":
            # Question 1: Total Result for Each Party in a PU
            polling_unit_id = "8"  # Example PU ID, replace with dynamic input
            results = (
                AnnouncedPuResults.objects.filter(polling_unit_uniqueid=polling_unit_id)
                .values("party_abbreviation")
                .annotate(total_score=Sum("party_score"))
            )
            result = f"Results for PU {polling_unit_id}: {list(results)}"

        elif question == "2":
            # Question 2: Total Result for All PU in an LGA
            lga_id = 5  # Example LGA ID, replace with dynamic input
            polling_units = PollingUnit.objects.filter(lga_id=lga_id).values_list(
                "uniqueid", flat=True
            )
            results = (
                AnnouncedPuResults.objects.filter(polling_unit_uniqueid__in=polling_units)
                .values("party_abbreviation")
                .annotate(total_score=Sum("party_score"))
            )
            result = f"Results for LGA {lga_id}: {list(results)}"

        elif question == "3":
            # Question 3: Add New Result for a PU
            new_result = AnnouncedPuResults.objects.create(
                polling_unit_uniqueid="8",  # Example PU ID
                party_abbreviation="ABC",  # Example Party
                party_score=200,  # Example Score
                entered_by_user="admin",
                date_entered="2025-01-18",
                user_ip_address="127.0.0.1",
            )
            result = f"New result added: {new_result.party_abbreviation} - {new_result.party_score}"

    return render(request, "logic.html", {"result": result})
