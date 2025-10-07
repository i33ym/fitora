# import json
# import base64
# from channels.generic.websocket import AsyncWebsocketConsumer
# from channels.db import database_sync_to_async
# from .services import analyze_meal_image

# class MealAnalysisConsumer(AsyncWebsocketConsumer):
#     async def connect(self):
#         user = self.scope.get('user')
        
#         if not user or user.is_anonymous:
#             await self.close(code=4001)
#             return
        
#         self.user = user
#         await self.accept()
#         await self.send(text_data=json.dumps({
#             'type': 'connection_established',
#             'message': 'Connected to meal analysis service'
#         }))
    
#     async def disconnect(self, close_code):
#         pass
    
#     async def receive(self, text_data):
#         try:
#             data = json.loads(text_data)
            
#             if data.get('type') == 'analyze_image':
#                 image_base64 = data.get('image')
                
#                 if not image_base64:
#                     await self.send(text_data=json.dumps({
#                         'type': 'error',
#                         'message': 'No image data provided'
#                     }))
#                     return
                
#                 await self.send(text_data=json.dumps({
#                     'type': 'analysis_started',
#                     'message': 'Analyzing your meal...'
#                 }))
                
#                 try:
#                     image_data = base64.b64decode(image_base64)
                    
#                     result = await self.analyze_image(image_data)
                    
#                     await self.send(text_data=json.dumps({
#                         'type': 'analysis_complete',
#                         'data': result
#                     }))
                    
#                 except Exception as e:
#                     await self.send(text_data=json.dumps({
#                         'type': 'error',
#                         'message': f'Analysis failed: {str(e)}'
#                     }))
#             else:
#                 await self.send(text_data=json.dumps({
#                     'type': 'error',
#                     'message': 'Unknown message type'
#                 }))
                
#         except json.JSONDecodeError:
#             await self.send(text_data=json.dumps({
#                 'type': 'error',
#                 'message': 'Invalid JSON format'
#             }))
#         except Exception as e:
#             await self.send(text_data=json.dumps({
#                 'type': 'error',
#                 'message': f'Server error: {str(e)}'
#             }))
    
#     @database_sync_to_async
#     def analyze_image(self, image_data):
#         return analyze_meal_image(image_data)

import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .services import analyze_meal_image

class MealAnalysisConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        user = self.scope.get('user')
        
        if not user or user.is_anonymous:
            await self.close(code=4001)
            return
        
        self.user = user
        await self.accept()
        await self.send(text_data=json.dumps({
            'type': 'connection_established',
            'message': 'Connected to meal analysis service'
        }))
    
    async def disconnect(self, close_code):
        pass
    
    async def receive(self, text_data=None, bytes_data=None):
        try:
            # Handle binary image data
            if bytes_data:
                await self.send(text_data=json.dumps({
                    'type': 'analysis_started',
                    'message': 'Analyzing your meal...'
                }))
                
                try:
                    result = await self.analyze_image(bytes_data)
                    
                    await self.send(text_data=json.dumps({
                        'type': 'analysis_complete',
                        'data': result
                    }))
                    
                except Exception as e:
                    await self.send(text_data=json.dumps({
                        'type': 'error',
                        'message': f'Analysis failed: {str(e)}'
                    }))
            
            # Handle text messages (for other commands if needed)
            elif text_data:
                data = json.loads(text_data)
                await self.send(text_data=json.dumps({
                    'type': 'info',
                    'message': 'Send image as binary data for analysis'
                }))
            
        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Invalid JSON format'
            }))
        except Exception as e:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': f'Server error: {str(e)}'
            }))
    
    @database_sync_to_async
    def analyze_image(self, image_data):
        return analyze_meal_image(image_data)