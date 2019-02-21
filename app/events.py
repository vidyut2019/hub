import datetime
import werkzeug.security
from flask import render_template, flash, redirect, request, url_for, jsonify,json
from app import app, db, api
from app.farer import authorizestaff
from config import Config
from app.models import Workshops,Talks,Contests,Registrations,User
from werkzeug.utils import secure_filename
from werkzeug.urls import url_parse
from flask_restplus import Resource, Api
from app.farer import auth_token

events = api.namespace('events', description="Events management")

@events.route('/workshops')
class events_workshops(Resource):

    # API Params: JSON([Standard])
    # Standard: IP, Sender ID
    # Returns: JSON array
    # Sends list of all Workshops
    # Accessible to all users
    def get(self):
        try:
            workshops = Workshops.query.all()
            responseObject = []
            for workshop in workshops:
                responseObject.append({
                    'id':workshop.id,
                    'title':workshop.title,
                    'plink':workshop.plink,
                    'short':workshop.short,
                    'department':workshop.department,
                    'fee':workshop.fee,
                    'seats':workshop.seats
                })
        except Exception as e:
            print(e)
            responseObject = {
                'status':'failure',
                'Message':'Error Occured'
            }
        return jsonify(responseObject)

    # API Params: JSON([Standard])
    # Standard: IP, Sender ID
    # Returns: JSON Status Code
    # Add Workshop
    # Permission: l3, l4 (Workshops)
    @api.doc(params = {
        'title':'Title',
        'plink':'Permanent Link',
        'short':'Short Description',
        'about':'Long Description in md',
        'prereq':'Prerequisites in md',
        'department':'Department',
        'theme':'Theme',
        'instructor':'Instructor Name',
        'abins':'About the Lead Instructor',
        'vidurl':'Video URL',
        'company':'Company Name',
        'lead':'Company Lead',
        'contact':'Contact No',
        'incharge':'Incharge V-ID',
        'support':'Supporter V-ID',
        'fee':'Workshop Fee',
        'seats':'No of Seats',
        'companylogo':'Company Logo location',
        'img1':'Image 1 location',
        'img2':'Image 2 location',
        'img3':'Image 3 location',
        })
    @authorizestaff(request,"workshop")
    def post(self):
        try:
            data = request.get_json()
            workshop = Workshops(
                title = data.get('title'),
                plink = data.get('plink'),
                short = data.get('short'),
                about = data.get('about'),
                department = data.get('department'),
                theme = data.get('theme'),
                vidurl = data.get('vidurl'),
                duration = data.get('duration'),
                org = data.get('org'),
                contact = data.get('contact'),
                fee = data.get('fee'),
                incharge = data.get('incharge'),
                seats = data.get('seats')
            )
            # Put a log in Farerlog
            db.session.add(workshop)
            db.session.commit()
            responseObject={
                'status':'success',
                'message':' Workshop Details Succefully Posted'
            }
        except Exception as e:
            print(e)
            # Send email
            responseObject = {
                'status':'fail',
                'message':'Error occured'
            }
        return jsonify(responseObject)

@events.route('/workshops/count')
class w_count(Resource):
    def get(self):
        w = Workshops.query.all()
        return len(w)

@events.route('/workshops/<int:id>')
class events_workshops_indv(Resource):

    # API Params: JSON([Standard])
    # Standard: IP, Sender ID
    # Returns: JSON Array
    # Send details of the Workshop
    def get(self, id):
        try:
            auth_t = auth_token(request)
            if auth_t:
                resp = User.decode_auth_token(auth_t)
            workshop = Workshops.query.filter_by(id=id).first()
            if workshop is not None:
                responseObject = {
                    'title':workshop.title,
                    'plink':workshop.plink,
                    'short':workshop.short,
                    'about':workshop.about,
                    'department':workshop.department,
                    'theme':workshop.theme,
                    'vidurl':workshop.vidurl,
                    'contact':workshop.contact,
                    'fee':workshop.fee,
                    'incharge':workshop.incharge,
                    'support':workshop.support,
                    'duration':workshop.duration,
                    'seats':workshop.seats,
                    'pub':workshop.pub
                }
            else:
                responseObject ={
                    'status':'fail',
                    'message':'invalid workshop id'
                }
        except Exception as e:
                print(e)
                # Send email
                responseObject = {
                    'status':'fail',
                    'message':'Error occured'
                }
        return jsonify(responseObject)

    # API Params: JSON([Standard])
    # Standard: IP, Sender ID
    # Returns: JSON Status Code
    # Edit details of the Workshop
    @authorizestaff(request,"workshops")
    @api.doc(params = {
        'title':'Title',
        'plink':'Permanent Link',
        'short':'Short Description',
        'about':'Long Description in md',
        'prereq':'Prerequisites in md',
        'department':'Department',
        'theme':'Theme',
        'instructor':'Instructor Name',
        'abins':'About the Lead Instructor',
        'vidurl':'Video URL',
        'org':'Organiser Name',
        'lead':'Organiser Lead',
        'contact':'Contact No',
        'incharge':'Incharge V-ID',
        'support':'Supporter V-ID',
        'fee':'Workshop Fee',
        'seats':'No of Seats',
        'companylogo':'Company Logo location',
        'img1':'Image 1 location',
        'img2':'Image 2 location',
        'img3':'Image 3 location',
        })
    @authorizestaff(request,"workshops")
    def put(self, id):
        try:
            workshop = Workshops.query.filter_by(id=id).first()
            if workshop is not None:
                data = request.get_json()
                workshop.title=data.get('title')
                workshop.about=data.get('about')
                workshop.org=data.get('org')
                workshop.fee=data.get('fee')
                db.session.commit()
                responseObject = {
                    'status':'success',
                    'message':'workshop details edited successfully'
                }
            else:
                responseObject = {
                    'status':'failed',
                    'message':'invalid workshop id'
                }
        except Exception as e:
            print(e)
            # Send email
            responseObject = {
                    'status':'fail',
                    'message':'Error occured'
            }
        return jsonify(responseObject)

    # API Params: JSON([Standard])
    # Standard: IP, Sender ID
    # Returns: JSON Status Code
    # Delete Workshop
    @authorizestaff(request,"workshops")
    def delete(self, id):
        try:
            workshop = Workshops.query.filter_by(id=id).first()
            if workshop is not None:
                db.session.delete(workshop)
                db.session.commit()
                responseObject = {
                    'status':'success',
                    'message':'workshop deleted'
                }
            else:
                responseObject = {
                    'status':'failed',
                    'message':'Invalid workshop id'
                }
        except Exception as e:
            print(e)
            # Send email
            responseObject = {
                    'status':'fail',
                    'message':'Error occured'
            }
        return jsonify(responseObject)

@events.route('/contests')
class events_contests(Resource):
    # API Params: JSON([Standard])
    # Standard: IP, Sender ID
    # Returns: JSON Array
    # Send list of all contests
    def get(self):
        try:
            contests = Contests.query.all()
            responseObject = []
            for contest in contests:
                responseObject.append({
                    'id':contest.id,
                    'title':contest.title,
                    'short':contest.short,
                    'pworth':contest.pworth,
                    'team_limit':contest.team_limit,
                    'fee':contest.fee
                })
        except Exception as e:
                print(e)
                # Send email
                responseObject = {
                    'status':'fail',
                    'message':'Error occured'
                }
        return jsonify(responseObject)

    # API Params: JSON([Standard])
    # Standard: IP, Sender ID
    # Returns: JSON Status
    # Add Contest
    @api.doc(params={
        'title':'Title',
        'short':'Short Description',
        'about':'Long Description in md',
        'rules':'Rules',
        'prereq':'Prerequisite in md',
        'organiser':'Organiser Name',
        'department':'Department No.',
        'prize1':'Prize 1',
        'prize2':'Prize 2',
        'prize3':'Prize 3',
        'pworth':'Total Prize Worth',
        'fee':'Entry Fee',
        'team_limit':'No of Team Members',
        'expense':'Expenses for internal use',
        'incharge':'Incharge V-ID',
    })
    @authorizestaff(request,"contests")
    def post(self):
        try:
            data = request.get_json()
            contest = Contests(
                title = data.get('title'),
                short = data.get('short'),
                pworth = data.get('pworth'),
                department = data.get('department'),
                team_limit=data.get('team_limit'),
                fee=data.get('fee'),
                incharge=data.get('incharge')
            )
            db.session.add(contest)
            db.session.commit()
            responseObject={
                'status':'success',
                'message':' Contest Details Succefully Posted'
            }
        except Exception as e:
            print(e)
            # Send email
            responseObject = {
                'status':'fail',
                'message':'Error occured'
            }
        return jsonify(responseObject)

@events.route('/contests/count')
class c_count(Resource):
    def get(self):
        c = Contests.query.all()
        return len(c)

@events.route('/contests/<int:id>')
class events_contests_indv(Resource):

    # API Params: JSON([Standard])
    # Standard: IP, Sender ID
    # Returns: JSON Array
    # Send details of the Contest
    def get(self, id):
        try:
            contest = Contests.query.filter_by(id=id).first()
            if contest is not None:
                responseObject = {
                    'title':contest.title,
                    'short':contest.short,
                    'pworth':contest.pworth,
                    'team_limit':contest.team_limit,
                    'fee':contest.fee,
                    'incharge':contest.incharge
                }
            else:
                responseObject ={
                    'status':'fail',
                    'message':'invalid contest id'
                }
        except Exception as e:
                print(e)
                # Send email
                responseObject = {
                    'status':'fail',
                    'message':'Error occured'
                }
        return jsonify(responseObject)

    # API Params: JSON([Standard])
    # Standard: IP, Sender ID
    # Returns: JSON Status Code
    # Edit details of the Contest
    @api.doc(params={
        'title':'Title',
        'short':'Short Description',
        'about':'Long Description in md',
        'rules':'Rules',
        'prereq':'Prerequisite in md',
        'organiser':'Organiser Name',
        'prize1':'Prize 1',
        'prize2':'Prize 2',
        'prize3':'Prize 3',
        'pworth':'Total Prize Worth',
        'fee':'Entry Fee',
        'team_limit':'No of Team Members',
        'expense':'Expenses for internal use',
        'incharge':'Incharge V-ID',
    })
    @authorizestaff(request,"contests")
    def put(self, id):
        try:
            contest = Contests.query.filter_by(id=id).first()
            if contest is not None:
                data = request.get_json()
                contest.title=data.get('title')
                contest.short=data.get('short')
                contest.pworth=data.get('pworth')
                contest.fee=data.get('fee')
                contest.incharge=data.get('incharge')
                contest.team_limit=data.get('team_limit')
                db.session.commit()
                responseObject = {
                    'status':'success',
                    'message':'Contest details edited successfully'
                }
            else:
                responseObject = {
                    'status':'failed',
                    'message':'invalid workshop id'
                }
        except Exception as e:
            print(e)
            # Send email
            responseObject = {
                    'status':'fail',
                    'message':'Error occured'
            }
        return jsonify(responseObject)

    # API Params: JSON([Standard])
    # Standard: IP, Sender ID
    # Returns: JSON Status Code
    # Delete Contest
    @authorizestaff(request,"contests")
    def delete(self, id):
        try:
            contest = Contests.query.filter_by(id=id).first()
            if contest is not None:
                db.session.delete(contest)
                db.session.commit()
                responseObject = {
                    'status':'success',
                    'message':'contest deleted'
                }
            else:
                responseObject = {
                    'status':'failed',
                    'message':'Invalid contest id'
                }
        except Exception as e:
            print(e)
            # Send email
            responseObject = {
                    'status':'fail',
                    'message':'Error occured'
            }
        return jsonify(responseObject)

@events.route('/talks')
class events_talks(Resource):

    # API Params: JSON([Standard])
    # Standard: IP, Sender ID
    # Returns: JSON Status
    # List all the Talks
    def get(self):
        try:
            talks = Talks.query.all()
            responseObject = []
            for talk in talks:
                responseObject.append({
                    'id':talk.id,
                    'title':talk.title,
                    'person':talk.person,
                    'fee':talk.fee
                })
        except Exception as e:
                print(e)
                # Send email
                responseObject = {
                    'status':'fail',
                    'message':'Error occured'
                }
        return jsonify(responseObject)

    # API Params: JSON([Standard])
    # Standard: IP, Sender ID
    # Returns: JSON Status
    # Add Talk
    @api.doc(params={
        'id':'Talk ID',
        'plink':'Permanent Link',
        'short':'Short Description',
        'about':'About Description',
        'person':'Name of the Person',
        'desig':'Designation',
        'contact':'Contact No',
        'picurl':'Picture of the Talk',
        'ppicurlsm':'Picture of the person small',
        'ppicurllr':'Picture of the person large',
        'fee':'fee for the talk',
        'incharge':'Incharge V-ID'
    })
    @authorizestaff(request,"talks")
    def post(self):
        try:
            data = request.get_json()
            talk = Talks(
                title=data.get('title'),
                short=data.get('short'),
                person=data.get('person'),
                desig=data.get('desig'),
                fee=data.get('fee'),
                incharge=data.get('incharge')
            )
            db.session.add(talk)
            db.session.commit()
            responseObject={
                'status':'success',
                'message':' Talk Details Succefully Posted'
            }
        except Exception as e:
            print(e)
            # Send email
            responseObject = {
                'status':'fail',
                'message':'Error occured'
            }
        return jsonify(responseObject)

@events.route('/talks/count')
class w_count(Resource):
    def get(self):
        t = Talks.query.all()
        return len(t)

@events.route('/talks/<int:id>')
class events_talks_indv(Resource):

    # API Params: JSON([Standard])
    # Standard: IP, Sender ID
    # Returns: JSON Array
    # Send details of the Talk
    def get(self, id):
        try:
            talk = Talks.query.filter_by(id=id).first()
            if talk is not None:
                responseObject = {
                    'title':talk.title,
                    'short':talk.short,
                    'person':talk.person,
                    'desig':talk.desig,
                    'fee':talk.fee,
                    'incharge':talk.incharge,
                }
            else:
                responseObject ={
                    'status':'fail',
                    'message':'invalid contest id'
                }
        except Exception as e:
                print(e)
                # Send email
                responseObject = {
                    'status':'fail',
                    'message':'Error occured'
                }
        return jsonify(responseObject)

    # API Params: JSON([Standard])
    # Standard: IP, Sender ID
    # Returns: JSON Status Code
    # Edit details of the Talk
    @api.doc(params={
        'id':'Talk ID',
        'plink':'Permanent Link',
        'short':'Short Description',
        'about':'About Description',
        'person':'Name of the Person',
        'desig':'Designation',
        'contact':'Contact No',
        'picurl':'Picture of the Talk',
        'ppicurlsm':'Picture of the person small',
        'ppicurllr':'Picture of the person large',
        'fee':'fee for the talk',
        'incharge':'Incharge V-ID'
    })
    @authorizestaff(request,"talks")
    def put(self, id):
        try:
            talk = Talks.query.filter_by(id=id).first()
            if talk is not None:
                data = request.get_json()
                talk.title=data.get('title')
                talk.short=data.get('short')
                talk.person=data.get('person')
                talk.desig=data.get('desig')
                talk.fee=data.get('fee')
                talk.incharge=data.get('incharge')
                db.session.commit()
                responseObject = {
                    'status':'success',
                    'message':'Contest details edited successfully'
                }
            else:
                responseObject = {
                    'status':'failed',
                    'message':'invalid workshop id'
                }
        except Exception as e:
            print(e)
            # Send email
            responseObject = {
                    'status':'fail',
                    'message':'Error occured'
            }
        return jsonify(responseObject)

    # API Params: JSON([Standard])
    # Standard: IP, Sender ID
    # Returns: JSON Status Code
    # Delete Talk
    @authorizestaff(request,"talks")
    def delete(self, id):
        try:
            talk = Talks.query.filter_by(id=id).first()
            if talk is not None:
                db.session.delete(talk)
                db.session.commit()
                responseObject = {
                    'status':'success',
                    'message':'Talk deleted'
                }
            else:
                responseObject = {
                    'status':'failed',
                    'message':'Invalid talk id'
                }
        except Exception as e:
            print(e)
            # Send email
            responseObject = {
                    'status':'fail',
                    'message':'Error occured'
            }
        return jsonify(responseObject)

@events.route('/registration')
class events_registration(Resource):

    def get(self):
        try:
            reg = Registrations.query.all()
            responseObject = []
            for regs in reg:
                responseObject.append({
                    'regid':regs.regid,
                    'vid':regs.vid,
                    'cat':regs.cat,
                    'eid':regs.eid,
                    'tid':regs.tid,
                    'pay_completed':regs.pay_completed,
                })
        except Exception as e:
            print(e)
            responseObject = {
                'status':'failure',
                'Message':'Error Occured'
            }
        return jsonify(responseObject)

    @api.doc(params={
        'cat':'Event Catagory',
        'eid':'Event ID',
        'tid':'Team ID'
    })

    def post(self):
        try:
            auth_t = auth_token(request)
            resp = User.decode_auth_token(auth_t)
            data = request.get_json()
            reg = Registrations.query.filter_by(vid=resp, cat=data.get('cat'), eid=data.get('eid')).first()
            if reg is not None:
                responseObject={
                    'status':'failure',
                    'message':'User already Registered'
                }
                return jsonify(responseObject)
            else:
                #Workshop Registration
                if data.get('cat') == 1:
                    w = Workshops.query.filter_by(id=data.get('eid')).first()
                    if w is not None:
                        seats = Registrations.query.filter_by(cat=1, eid=data.get('eid')).count()
                        if seats < w.seats:
                            r = Registrations(vid=resp, cat=1, eid=data.get('eid'))
                            db.session.add(r)
                            db.session.commit()
                            responseObject={
                                'status':'success',
                                'message':'Registration Success'
                            }
                        else:
                            responseObject={
                                'status':'failure',
                                'message':'No seats'
                            }
                    else:
                        responseObject = {
                            'status':'failure',
                            'message':'Invalid workshop ID'
                        }
                    return jsonify(responseObject)
                elif data.get('cat') == 2:
                    c = Contests.query.filter_by(id=data.get('eid')).first()
                    if c is not None:
                        if c.team_limit is 1:
                            r = Registrations(vid=resp, cat=2, eid=data.get('eid'))
                            db.session.add(r)
                            db.session.commit()
                            responseObject={
                                'status':'success',
                                'message':'Registration Success'
                            }
                        elif data.get('tid') is None:
                            print("team id gen")
                            tid = werkzeug.security.pbkdf2_hex(resp,resp ,iterations=50000, keylen=5, hashfunc=None)
                            print(tid)
                            r = Registrations(vid=resp, cat=2, eid=data.get('eid'), tid=tid)
                            db.session.add(r)
                            db.session.commit()
                            responseObject={
                                'status':'success',
                                'message':'Registration Success'
                            }
                        else:
                            team = Registrations.query.filter_by(cat=2, eid=data.get('eid'), tid=data.get('tid')).count()
                            if count < c.team_limit:
                                r = Registrations(vid=resp, cat=2, eid=data.get('eid'), tid=form.data.get('eid'))
                                db.session.add(r)
                                db.session.commit()
                                responseObject={
                                    'status':'success',
                                    'message':'Registration Success'
                                }
                            else:
                                responseObject={
                                    'status':'failure',
                                    'message':'Team is full'
                                }
                    else:
                        responseObject = {
                            'status':'failure',
                            'message':'Invalid Event ID'
                        }
                    return jsonify(responseObject)
                elif data.get('cat') == 3:
                    t = Talks.query.filter_by(id=data.get('eid')).first()
                    if t is not None:
                        seats = Registrations.query.filter_by(cat=3, eid=data.get('eid')).count()
                        if seats < w.seats:
                            r = Registrations(vid=resp, cat=3, eid=data.get('eid'))
                            db.session.add(r)
                            db.session.commit()
                            responseObject={
                                'status':'success',
                                'message':'Registration Success'
                            }
                        else:
                            responseObject={
                                'status':'failure',
                                'message':'No seats'
                            }
                    else:
                        responseObject = {
                            'status':'failure',
                            'message':'Invalid Talk ID'
                        }
                    return jsonify(responseObject)
                else:
                    responseObject = {
                        'status':'Failure',
                        'message':'Invalid Category'
                    }
                    return jsonify(responseObject);
        except Exception as e:
            print(e)
            responseObject={
                'status':'Failure',
                'message':'Error Occured'
            }
            return jsonif(responseObject)

@events.route('/registration/workshops/<int:id>')
class events_registration_workshop(Resource):

    # API Params: JSON([Standard])
    # Standard: IP, Sender ID
    # Returns: JSON Array
    # Send details of the Talk
    def get(self, id):
        try:
            reg = Registrations.query.filter_by(cat=1,eid=id)
            if reg is not None:
                responseObject = []
                for regs in reg:
                    responseObject.append({
                        'regid':regs.regid,
                        'vid':regs.vid,
                        'cat':regs.cat,
                        'eid':regs.eid,
                        'pay_completed':regs.pay_completed,
                    })
            else:
                responseObject ={
                    'status':'fail',
                    'message':'invalid contest id'
                }
        except Exception as e:
                print(e)
                # Send email
                responseObject = {
                    'status':'fail',
                    'message':'Error occured'
                }
        return jsonify(responseObject)

@events.route('/registration/contests/<int:id>')
class events_registration_contests(Resource):

    # API Params: JSON([Standard])
    # Standard: IP, Sender ID
    # Returns: JSON Array
    # Send details of the Talk
    def get(self, id):
        try:
            reg = Registrations.query.filter_by(cat=2,eid=id)
            if reg is not None:
                responseObject = []
                for regs in reg:
                    responseObject.append({
                        'regid':regs.regid,
                        'vid':regs.vid,
                        'cat':regs.cat,
                        'eid':regs.eid,
                        'tid':regs.tid,
                        'pay_completed':regs.pay_completed,
                    })
            else:
                responseObject ={
                    'status':'fail',
                    'message':'invalid contest id'
                }
        except Exception as e:
                print(e)
                # Send email
                responseObject = {
                    'status':'fail',
                    'message':'Error occured'
                }
        return jsonify(responseObject)

@events.route('/registration/talks/<int:id>')
class events_registration_talks(Resource):

    # API Params: JSON([Standard])
    # Standard: IP, Sender ID
    # Returns: JSON Array
    # Send details of the Talk
    def get(self, id):
        try:
            reg = Registrations.query.filter_by(cat=3,eid=id)
            if reg is not None:
                responseObject = []
                for regs in reg:
                    responseObject.append({
                        'regid':regs.regid,
                        'vid':regs.vid,
                        'cat':regs.cat,
                        'eid':regs.eid,
                        'pay_completed':regs.pay_completed,
                    })
            else:
                responseObject ={
                    'status':'fail',
                    'message':'invalid contest id'
                }
        except Exception as e:
                print(e)
                # Send email
                responseObject = {
                    'status':'fail',
                    'message':'Error occured'
                }
        return jsonify(responseObject)
