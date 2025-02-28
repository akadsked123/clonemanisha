class MeetingParser:
    def parse_meeting_time(self, meeting_time):
        """
        Parse meeting time into face-to-face and online components based on the provided pattern.
        """
        import re
        days_pattern = re.findall(r"[A-Z]\*?[A-Z_]*", meeting_time.split(" ")[0])
        time = " ".join(meeting_time.split(" ")[1:])
        days = {"online": [], "face_to_face": []}

        for pattern in days_pattern:
            if "*" in pattern:
                # Handle patterns like "MW*_" or "T*TH"
                base_day = re.findall(r"[A-Z]", pattern)
                for i, day in enumerate(base_day):
                    if "*" in pattern and "*" in pattern[i:]:
                        days["online"].append(day)
                    else:
                        days["face_to_face"].append(day)
            else:
                # Handle normal face-to-face patterns without "*"
                days["face_to_face"].extend(list(pattern))

        return days, time

# Data
meeting_times = [
    "M*W_", "MW*_", "M*W_", "MW*_", "M*W_", "MW*_", "M*W_", "MW*_", 
    "T*TH", "TTH*", "T*TH", "TTH*", "T*TH", "TTH*", "T*TH", "TTH*", 
    "W*F_", "WF*_", "W*F_", "WF*_", "W*F_", "WF*_", "W*F_", "WF*_", 
    "W*F_", "WF*_", "T*TH", "TTH*", "T*TH", "TTH*", "T*TH", "TTH*", 
    "T*TH", "TTH*", "T*TH", "TTH*", "T*TH", "TTH*", "T*TH", "TTH*"
]

# Create an instance of MeetingParser
parser = MeetingParser()

# Process and print the results
for meeting_time in meeting_times:
    days, time = parser.parse_meeting_time(meeting_time)
    print(f"Meeting Time: {meeting_time}")
    print(f"Online Days: {days['online']}")
    print(f"Face-to-Face Days: {days['face_to_face']}")
    print()