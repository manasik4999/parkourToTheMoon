import requests
import time
import json
from constants import base_url, candidate_id

class MegaverseAPI:
    def __init__(self, base_url, candidate_id):
        self.base_url = base_url
        self.candidate_id = candidate_id

    def _post_or_del_with_retry(self, endpoint, method, data=None):
        url = f"{self.base_url}/{endpoint}"
        retries = 5
        for i in range(retries):
            try:
                if method == "post":
                    response = requests.post(url, json=data)
                elif method == "delete":
                    response = requests.delete(url, json=data)
                else:
                    raise ValueError(f"Unsupported method: {method}")

                if response.status_code == 429:
                    wait_time = 2 ** i  # Exponential backoff
                    print(f"Rate limit exceeded. Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                else:
                    response.raise_for_status()
                    return response.json()

            except requests.exceptions.HTTPError as e:
                print(f"HTTP error occurred: {e}")
                if i < retries - 1:
                    print("Retrying...")
                    time.sleep(2 ** i)
                else:
                    raise

            except Exception as e:
                print(f"An error occurred: {e}")
                raise

        raise Exception("Failed to complete request after several retries")

    def create_polyane(self, row, column):
        data = {
            "row": row,
            "column": column,
            "candidateId": self.candidate_id
        }
        return self._post_or_del_with_retry("polyanets","post", data)

    def create_soloon(self, row, column, color):
        data = {
            "row": row,
            "column": column,
            "candidateId": self.candidate_id,
            "color": color
        }
        return self._post_or_del_with_retry("soloons", "post", data)

    def create_cometh(self, row, column, direction):
        data = {
            "row": row,
            "column": column,
            "candidateId": self.candidate_id,
            "direction": direction
        }
        return self._post_or_del_with_retry("comeths", "post", data)

    def del_object(self, type_of_comet, row, column):
        data = {
            "row": row,
            "column": column,
            "candidateId": self.candidate_id
        }
        return self._post_or_del_with_retry(type_of_comet, "delete", data)

class MegaverseBuilder:
    def __init__(self, api, action):
        self.api = api
        self.action = action

    def parse_and_build(self, file_path):
        with open(file_path, 'r') as f:
            goal_map = json.load(f)

        color_mapping = {
            "WHITE_SOLOON": "white",
            "BLUE_SOLOON": "blue",
            "RED_SOLOON": "red",
            "PURPLE_SOLOON": "purple"
        }
        direction_mapping = {
            "UP_COMETH": "up",
            "DOWN_COMETH": "down",
            "LEFT_COMETH": "left",
            "RIGHT_COMETH": "right"
        }
        
        if self.action=='create':
          #creating logo
          for row_idx, row in enumerate(goal_map):
              for col_idx, cell in enumerate(row):
                  if cell == "POLYANET":
                      self.api.create_polyane(row_idx, col_idx)
                  elif cell in color_mapping:
                      self.api.create_soloon(row_idx, col_idx, color_mapping[cell])
                  elif cell in direction_mapping:
                      self.api.create_cometh(row_idx, col_idx, direction_mapping[cell])

        elif self.action=='delete':
          #deleting logo
          for row_idx, row in enumerate(goal_map):
              for col_idx, cell in enumerate(row):
                  if cell == "POLYANET":
                      self.api.del_object("polyanets", row_idx, col_idx)
                  elif cell in color_mapping:
                      self.api.del_object("soloons", row_idx, col_idx)
                  elif cell in direction_mapping:
                      self.api.del_object("comeths", row_idx, col_idx)
        else:
          print("This action does not exist. Available actions are 'create' and 'delete'")


api = MegaverseAPI(base_url, candidate_id)
action="create"
builder = MegaverseBuilder(api,action)

file_path = 'goal.json'
builder.parse_and_build(file_path)
