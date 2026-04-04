class GestureMapper:

    def __init__(self):
        self.mapping = {}

    

    def add_mapping(self, face, hand, image):
        self.mapping[(face, hand)] = image

    
    def get_image(self, face, hand):

        # exact match
        if (face, hand) in self.mapping:
            return self.mapping[(face, hand)]

        # face only
        if (face, "no_hand") in self.mapping:
            return self.mapping[(face, "no_hand")]

        # hand only
        if ("neutral", hand) in self.mapping:
            return self.mapping[("neutral", hand)]

        
        return None