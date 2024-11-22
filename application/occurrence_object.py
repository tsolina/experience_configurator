import experience as exp

class OccurenceObject:
    def __init__(self, occurrence: exp.VPMOccurrence):
        # Check the type of occurrence to determine if it's a root occurrence or regular occurrence
        if isinstance(occurrence, exp.VPMRootOccurrence):
            self.occurrence = occurrence
            self.reference = occurrence.reference_root_occurrence_of()
            self.id = occurrence.reference_root_occurrence_of().id()
        elif isinstance(occurrence, exp.VPMOccurrence):
            self.occurrence = occurrence
            self.reference = occurrence.instance_occurrence_of().reference_instance_of()
            self.id = occurrence.instance_occurrence_of().reference_instance_of().id()
        else:
            raise ValueError("Invalid occurrence type provided")