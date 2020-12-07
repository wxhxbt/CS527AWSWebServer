# -*- coding: utf-8 -*-

# This sample demonstrates handling intents from an Alexa skill using the Alexa Skills Kit SDK for Python.
# Please visit https://alexa.design/cookbook for additional examples on implementing slots, dialog management,
# session persistence, api calls, and more.
# This sample is built using the handler classes approach in skill builder.
import logging
import ask_sdk_core.utils as ask_utils

from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.dispatch_components import AbstractExceptionHandler
from ask_sdk_core.handler_input import HandlerInput

from ask_sdk_model import Response
import requests
import random

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class LaunchRequestHandler(AbstractRequestHandler):
    """Handler for Skill Launch."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool

        return ask_utils.is_request_type("LaunchRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        r = requests.get('http://ec2-18-217-249-18.us-east-2.compute.amazonaws.com:8000/search_text/', params={'slc':'rds', 'txt':'select "Home." as Welcome'})
        if r.status_code == 200:
            speak_output = "Welcome, what query would you like to try? Or you can say, help."
        else:
            speak_output = 'Sorry. There is some problem.'

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )


class HelloWorldIntentHandler(AbstractRequestHandler):
    """Handler for Hello World Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("HelloWorldIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        r = requests.get('http://ec2-18-217-249-18.us-east-2.compute.amazonaws.com:8000/search_text/', params={'slc':'rds', 'txt':'select "Nice to meet you." as Hello'})
        if r.status_code == 200:
            speak_output = "Nice to meet you. I mean, virtually. What command would you like to try?"
        else:
            speak_output = 'Sorry. There is some problem.'
        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )


suc_response = {
    1: "Ok. I have fetched the data.",
    2: "No problem. I'll do the job.",
    3: "Understood. Getting the data."
}

aggre_keyword = ['count', 'sum', 'avg', 'max', 'min']

class SQLIntentHandler(AbstractRequestHandler):
    """Handler for SQL Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("SQLIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        slots = handler_input.request_envelope.request.intent.slots
        attr1, attr2, attr3, attr4 = None, None, None, None
        
        table = slots['table'].resolutions.resolutions_per_authority[0].values[0].value.name
        attr1 = slots['attribute'].resolutions.resolutions_per_authority[0].values[0].value.name
        if slots['attribute_two'].resolutions:
            attr2 = slots['attribute_two'].resolutions.resolutions_per_authority[0].values[0].value.name
        if slots['attribute_three'].resolutions:
            attr3 = slots['attribute_three'].resolutions.resolutions_per_authority[0].values[0].value.name
        if slots['attribute_four'].resolutions:
            attr4 = slots['attribute_four'].resolutions.resolutions_per_authority[0].values[0].value.name
        sql = 'select '
        if attr1 and attr1 not in aggre_keyword:
            attr1 = attr1 if attr1 != 'star' else '*'
            sql += attr1  + ','
        if attr2 and attr2 not in aggre_keyword:
            attr2 = attr2 if attr2 != 'star' else '*'
            sql += (attr2 + ',') if attr1 not in aggre_keyword else (attr1+'('+attr2+')'+',')
        if attr3 and attr3 not in aggre_keyword:
            attr3 = attr3 if attr3 != 'star' else '*'
            sql += (attr3 + ',') if attr2 not in aggre_keyword else (attr2+'('+attr3+')'+',')
        if attr4 and attr4 not in aggre_keyword:
            attr4 = attr4 if attr4 != 'star' else '*'
            sql += (attr4 + ',') if attr3 not in aggre_keyword else (attr3+'('+attr4+')'+',')
        
        sql = sql[:-1] + ' from ' + table
        if slots['table_two'].resolutions:
            sql += ' natural join ' + slots['table_two'].resolutions.resolutions_per_authority[0].values[0].value.name
        if slots['table_three'].resolutions:
            sql += ' natural join ' + slots['table_three'].resolutions.resolutions_per_authority[0].values[0].value.name
        
        if slots['filter_attr'].value and slots['operator'].value and slots['filter_value'].value:
            sql += (' where ' + slots['filter_attr'].resolutions.resolutions_per_authority[0].values[0].value.name + slots['operator'].resolutions.resolutions_per_authority[0].values[0].value.name + slots['filter_value'].value)
        
        if slots['group_attr'].resolutions:
            sql += ' group by ' + slots['group_attr'].resolutions.resolutions_per_authority[0].values[0].value.name
            if slots['having_attr_one'].resolutions:
                sql += ' having ' + slots['having_attr_one'].resolutions.resolutions_per_authority[0].values[0].value.name
                if slots['having_attr_two'].resolutions:
                    hav_attr_t = slots['having_attr_two'].resolutions.resolutions_per_authority[0].values[0].value.name
                    hav_attr_t = hav_attr_t if hav_attr_t != 'star' else '*'
                    sql += '(' + hav_attr_t + ')'
                sql += slots['having_op'].resolutions.resolutions_per_authority[0].values[0].value.name + slots['having_value'].value
        
        if slots['order_num'].value and slots['order_seq'].resolutions:
            sql += ' order by ' + slots['order_num'].value + ' ' + slots['order_seq'].resolutions.resolutions_per_authority[0].values[0].value.name
        
        if slots['number'].value:
            sql += (' limit ' + slots['number'].value)
        
        print(sql)
        r = requests.get('http://ec2-18-217-249-18.us-east-2.compute.amazonaws.com:8000/search_text/', params={'slc':'rds', 'txt':sql})
        if r.status_code == 200:
            speak_output = suc_response[random.randint(1, 3)]
        else:
            speak_output = 'Sorry. There is some problem.'
        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )


class AisleDepAdvIntentHandler(AbstractRequestHandler):
    """Handler for advanced query Intent of aisles and departments."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("AisleDepAdvIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        slots = handler_input.request_envelope.request.intent.slots
        if slots['target'].value and slots['seq'].value:
            tar = slots['target'].resolutions.resolutions_per_authority[0].values[0].value.name
            seq = slots['seq'].resolutions.resolutions_per_authority[0].values[0].value.name
            
            sql = 'select '
            sql += 'aisle_id, aisle, count(*) as `number of products`' if tar == 'AISLE' else 'department_id, department, count(*) as `number of products`'
            sql += ' from PRODUCT natural join ' + tar
            sql += ' group by 1'
            sql += ' order by 3 ' + seq
            sql += ' limit ' + (slots['num'].value if slots['num'].value else '1')
        
        if slots['aisles'].value:
            sql = f"select aisle, product_id, product_name from PRODUCT natural join AISLE where aisle = '{slots['aisles'].value}'"
        r = requests.get('http://ec2-18-217-249-18.us-east-2.compute.amazonaws.com:8000/search_text/', params={'slc':'rds', 'txt':sql})
        if r.status_code == 200:
            speak_output = suc_response[random.randint(1, 3)]
        else:
            speak_output = 'Sorry. There is some problem.'
        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )


class ProductAdvIntentHandler(AbstractRequestHandler):
    """Handler for advanced query Intent of products."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("ProductAdvIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        slots = handler_input.request_envelope.request.intent.slots
        if slots['seq'].value:
            seq = slots['seq'].resolutions.resolutions_per_authority[0].values[0].value.name
            
            sql = 'select product_id, product_name, count(*) as `number of sales` from ORDER_PRODUCT natural join PRODUCT natural join DEPARTMENT'
            if slots['dep'].value:
                sql += f" where department = '{slots['dep'].value}'"
            sql += ' group by 1'
            sql += ' order by 3 ' + seq
            sql += ' limit ' + (slots['num'].value if slots['num'].value else '1')
        
        if slots['reorder'].value:
            # sql = 'select product_id, product_name, count(*) as `number of buybacks` from ORDER_PRODUCT natural join PRODUCT natural join DEPARTMENT'
            # sql += ' where reordered = 1'
            # if slots['dep'].value:
            #     sql += f" and department = '{slots['dep'].value}'"
            # sql += ' group by 1'
            # sql += ' order by 3 ' + seq
            # sql += ' limit ' + (slots['num'].value if slots['num'].value else '1')
            sql = "select product_id, product_name, total, numOfReordered, (numOfReordered / total) as reorderedRatio \
                from (select product_id, count(*) as total from ORDER_PRODUCT group by 1) as a \
                natural join (select product_id, count(*) as numOfReordered from ORDER_PRODUCT where reordered = 1 group by 1) as b natural join PRODUCT natural join DEPARTMENT"
            sql += " where total >= 100"
            if slots['dep'].value:
                sql += f" and department = '{slots['dep'].value}'"
            sql += " order by 5 " + seq
            sql += ' limit ' + (slots['num'].value if slots['num'].value else '1')
            # print(sql)
        
        if slots['product'].value:
            sql = f"select aisle_id, aisle, product_name from PRODUCT natural join AISLE where lower(product_name) = '{slots['product'].value}'"
        
        r = requests.get('http://ec2-18-217-249-18.us-east-2.compute.amazonaws.com:8000/search_text/', params={'slc':'rds', 'txt':sql})
        if r.status_code == 200:
            speak_output = suc_response[random.randint(1, 3)]
        else:
            speak_output = 'Sorry. There is some problem.'
        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )


class HelpIntentHandler(AbstractRequestHandler):
    """Handler for Help Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("AMAZON.HelpIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        r = requests.get('http://ec2-18-217-249-18.us-east-2.compute.amazonaws.com:8000/search_text/', params={'slc':'rds', 'txt':'select * from help'})
        speak_output = "You can find some instructions in the web page. How can I help?"
        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )


class CancelOrStopIntentHandler(AbstractRequestHandler):
    """Single handler for Cancel and Stop Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return (ask_utils.is_intent_name("AMAZON.CancelIntent")(handler_input) or
                ask_utils.is_intent_name("AMAZON.StopIntent")(handler_input))

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "Goodbye!"

        return (
            handler_input.response_builder
                .speak(speak_output)
                .response
        )


class SessionEndedRequestHandler(AbstractRequestHandler):
    """Handler for Session End."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_request_type("SessionEndedRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response

        # Any cleanup logic goes here.

        return handler_input.response_builder.response


class IntentReflectorHandler(AbstractRequestHandler):
    """The intent reflector is used for interaction model testing and debugging.
    It will simply repeat the intent the user said. You can create custom handlers
    for your intents by defining them above, then also adding them to the request
    handler chain below.
    """
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_request_type("IntentRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        intent_name = ask_utils.get_intent_name(handler_input)
        speak_output = "You just triggered " + intent_name + "."

        return (
            handler_input.response_builder
                .speak(speak_output)
                # .ask("add a reprompt if you want to keep the session open for the user to respond")
                .response
        )


class CatchAllExceptionHandler(AbstractExceptionHandler):
    """Generic error handling to capture any syntax or routing errors. If you receive an error
    stating the request handler chain is not found, you have not implemented a handler for
    the intent being invoked or included it in the skill builder below.
    """
    def can_handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> bool
        return True

    def handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> Response
        logger.error(exception, exc_info=True)

        speak_output = "Sorry, I had trouble doing what you asked. Please try again."

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )

# The SkillBuilder object acts as the entry point for your skill, routing all request and response
# payloads to the handlers above. Make sure any new handlers or interceptors you've
# defined are included below. The order matters - they're processed top to bottom.


sb = SkillBuilder()

sb.add_request_handler(LaunchRequestHandler())
sb.add_request_handler(SQLIntentHandler())
sb.add_request_handler(AisleDepAdvIntentHandler())
sb.add_request_handler(ProductAdvIntentHandler())
sb.add_request_handler(HelloWorldIntentHandler())
sb.add_request_handler(HelpIntentHandler())
sb.add_request_handler(CancelOrStopIntentHandler())
sb.add_request_handler(SessionEndedRequestHandler())
sb.add_request_handler(IntentReflectorHandler()) # make sure IntentReflectorHandler is last so it doesn't override your custom intent handlers

sb.add_exception_handler(CatchAllExceptionHandler())

lambda_handler = sb.lambda_handler()