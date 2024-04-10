from myapp.models.student import *
from sqlalchemy import func, select,text,exists,or_


query = query.filter(TuitionFee.payer_id != None)
