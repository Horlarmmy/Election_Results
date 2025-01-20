from django.shortcuts import render
from django.db.models import Sum
from .models import AnnouncedPuResults, AnnouncedLgaResults, PollingUnit, Lga
from django.utils.timezone import now

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
    lgas = Lga.objects.all()  # Fetch all LGAs to populate the dropdown
    lga_name = ""

    if request.method == "POST":
        lga_id = request.POST.get("lga_id")  # Get the selected LGA ID
        #use id to get the name of the LGA
        lga_name = Lga.objects.filter(lga_id=lga_id).values_list("lga_name", flat=True).first()
        
        # Get unique IDs of polling units in the selected LGA
        polling_units = list(PollingUnit.objects.filter(lga_id=lga_id).values_list("uniqueid", flat=True))
        
        # Sum the party scores for all polling units in the LGA
        party_scores = AnnouncedPuResults.objects.filter(polling_unit_uniqueid__in=polling_units).values(
            "party_abbreviation"
        ).annotate(total_score=Sum("party_score"))
        
    return render(request, "question_2.html", {"party_scores": party_scores, "lgas": lgas, "lga_name": lga_name})


def question_3(request):
    message = ""
    if request.method == "POST":
        lga_name = request.POST.get("lga_name")
        polling_unit_id = request.POST.get("polling_unit_id")
        ward_id = request.POST.get("ward_id")
        party_results = [
            {
                "party_abbreviation": request.POST.get(f"party_{i}_abbreviation"),
                "party_score": request.POST.get(f"party_{i}_score"),
            }
            for i in range(1, 10)
        ]

        # Get the LGA ID from the LGA name
        lga_id = Lga.objects.filter(lga_name=lga_name).values_list("lga_id", flat=True).first()

        if not lga_id:
            message = f"LGA '{lga_name}' not found."
        else:
            # Create a new PollingUnit if it doesn't exist
            polling_unit, created = PollingUnit.objects.get_or_create(
                polling_unit_id=polling_unit_id,
                lga_id=lga_id,
                ward_id=ward_id,
                defaults={
                    "polling_unit_name": f"Polling Unit {polling_unit_id}",
                    "entered_by_user": "admin",
                    "date_entered": now(),
                    "user_ip_address": request.META.get("REMOTE_ADDR"),
                },
            )

            # Add results for each party
            for result in party_results:
                if result["party_abbreviation"] and result["party_score"]:
                    AnnouncedPuResults.objects.create(
                        polling_unit_uniqueid=polling_unit.uniqueid,
                        party_abbreviation=result["party_abbreviation"],
                        party_score=int(result["party_score"]),
                        entered_by_user="admin",
                        date_entered=now(),
                        user_ip_address=request.META.get("REMOTE_ADDR"),
                    )
            message = f"Results successfully added for Polling Unit ID {polling_unit_id}."

    return render(request, "question_3.html", {"message": message, "party_range": range(1, 10)})



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
