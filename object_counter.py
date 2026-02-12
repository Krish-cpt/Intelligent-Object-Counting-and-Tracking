# object_counter.py

class ObjectCounter:
    def __init__(self, line_position):
        self.line_position = line_position
        self.count = 0
        self.past_positions = {}

    def update(self, objects):
        # remove past positions for objects that are no longer tracked
        existing_ids = set(objects.keys())
        for old_id in list(self.past_positions.keys()):
            if old_id not in existing_ids:
                del self.past_positions[old_id]

        for (objectID, centroid) in objects.items():
            cx, cy = centroid

            if objectID not in self.past_positions:
                self.past_positions[objectID] = cy

            if self.past_positions[objectID] < self.line_position <= cy:
                self.count += 1

            self.past_positions[objectID] = cy

        return self.count
