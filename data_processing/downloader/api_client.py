import os
import json
from .dataset_io import GraphQLClient

class AnnotationDataDownloader:
    def __init__(self, config):
        """Initialize downloader.

        Credentials for iMean are read from the environment variables
        ``IMEAN_USERNAME`` and ``IMEAN_PASSWORD``.

        Args:
            config: Configuration dictionary
        """
        self.challenge_id = config.get('challenge_id')
        self.save_path = config.get('save_path')
        
            
        self.client = GraphQLClient()
        
    def download_annotations(self):
        """Download annotation data from iMean platform"""
        try:
            # Login
            self.client.login()
            
            # Ensure save path exists
            os.makedirs(self.save_path, exist_ok=True)
            
            # Download data
            self.client.export_atom_flows(
                challenge_id=self.challenge_id,
                save_path=self.save_path
            )
            
            # Read downloaded JSON files
            json_files = [f for f in os.listdir(self.save_path) 
                         if f.endswith('.json')]
            
            if not json_files:
                raise Exception("No JSON files found in the downloaded data")
                
            data = []
            for json_file in json_files:
                file_path = os.path.join(self.save_path, json_file)
                with open(file_path, 'r', encoding='utf-8') as f:
                    data.extend(json.load(f))
                    
            return data
            
        except Exception as e:
            raise Exception(f"Failed to download annotations: {str(e)}")
    
    def save_raw_data(self, data, output_path):
        """Save raw data to specified path"""
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False) 
