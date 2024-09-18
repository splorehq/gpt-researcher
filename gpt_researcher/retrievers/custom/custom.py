from typing import Any, Dict, List, Optional
import requests
import os
import json

class CustomRetriever:
    """
    Custom API Retriever
    """

    def __init__(self, query: str):
        # self.endpoint = os.getenv('RETRIEVER_ENDPOINT')
        # if not self.endpoint:
        #     raise ValueError("RETRIEVER_ENDPOINT environment variable not set")

        self.params = self._populate_params()
        self.query = query

    def _populate_params(self) -> Dict[str, Any]:
        """
        Populates parameters from environment variables prefixed with 'RETRIEVER_ARG_'
        """
        return {
            key[len('RETRIEVER_ARG_'):].lower(): value
            for key, value in os.environ.items()
            if key.startswith('RETRIEVER_ARG_')
        }

    # def search(self, max_results: int = 5) -> Optional[List[Dict[str, Any]]]:
    #     """
    #     Performs the search using the custom retriever endpoint.

    #     :param max_results: Maximum number of results to return (not currently used)
    #     :return: JSON response in the format:
    #         [
    #           {
    #             "url": "http://example.com/page1",
    #             "raw_content": "Content of page 1"
    #           },
    #           {
    #             "url": "http://example.com/page2",
    #             "raw_content": "Content of page 2"
    #           }
    #         ]
    #     """
    #     try:
    #         response = requests.get(self.endpoint, params={**self.params, 'query': self.query})
    #         response.raise_for_status()
    #         return response.json()
    #     except requests.RequestException as e:
    #         print(f"Failed to retrieve search results: {e}")
    #         return None
    def make_post_request(self, url, data):
        try:
            headers = {'Content-Type': 'application/json'}
            response = requests.post(url, data=json.dumps(data), headers=headers)
            response.raise_for_status()  # Raise an exception for HTTP errors
            return response.json()  # Return the response as JSON
        except requests.exceptions.RequestException as e:
            print(f"An error occurred: {e}")
            return None
    
    def search(self, max_results: int = 5) -> Optional[List[Dict[str, Any]]]:
        """
        Performs the search using the custom retriever endpoint.

        :param max_results: Maximum number of results to return (not currently used)
        :return: JSON response in the format:
            [
              {
                "url": "http://example.com/page1",
                "raw_content": "Content of page 1"
              },
              {
                "url": "http://example.com/page2",
                "raw_content": "Content of page 2"
              }
            ]
        """
        try:
            base_id = "STEN2imEGLyHBfz7hgYv28CQ1LjNaC9"
            agent_id = "ABSC2imFB6aPuRSRnQtDp1qXmcI6eat"
            SPLORE_URL = "https://api.splore.ai/api/v1/retrieve"

            data = {
                "query": self.query,
                "base_id": base_id,
                "agent_id": agent_id
            }
            
            response = self.make_post_request(SPLORE_URL, data)
            response = response["docs"][:5]
            final_results = []
            for doc in response:
                result = {"url": doc["metadata"]["external_link"], "raw_content": doc["snippet"]}
                final_results.append(result)
            
            return final_results
        
        except requests.RequestException as e:
            print(f"Failed to retrieve search results: {e}")
            return None
        
    def search(self, max_results=7, search_depth=None, include_domains=None, exclude_domains=None):
        """
        Performs the search using the custom retriever endpoint.

        :param max_results: Maximum number of results to return (not currently used)
        :return: JSON response in the format:
            [
              {
                "url": "http://example.com/page1",
                "raw_content": "Content of page 1"
              },
              {
                "url": "http://example.com/page2",
                "raw_content": "Content of page 2"
              }
            ]
        """
        max_results = 5
        try:
            base_id = "STEN2lGcs1cZYGtI1Fgr9Mc6D692jiX"
            agent_id = "ABSC2lGm7ILu1bV8yLFPGfsrPtaFuYv"
            SPLORE_URL = "https://api.splore.ai/api/v1/retrieve"

            data = {
                "query": self.query,
                "base_id": base_id,
                "agent_id": agent_id
            }
            
            response = self.make_post_request(SPLORE_URL, data)

            print("**************** SPLORE Response **********", response)

            if response and "docs" in response and isinstance(response["docs"], list) and len(response["docs"]) > 0:
                response = response["docs"][:max_results]
            else:
                print("No documents found in the response.")
                return None
            
            final_results = []
            for doc in response:
                result = {"url": doc["metadata"]["external_link"], "raw_content": doc["snippet"]}
                final_results.append(result)
            
            return final_results
        
        except requests.RequestException as e:
            print(f"Failed to retrieve search results: {e}")
            return None