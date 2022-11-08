import unittest
import flask_testing
import json
from app import app, db, Skill,Course,Role,Role_Skill,Course_Skill,LearningJourney,Learning_Journey_Courses,Registration

#logic differs , but the assertions and lib we are using for both unit and integration tests is the same
#only the implementation will vary 
class TestApp(flask_testing.TestCase):
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite://"
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {}
    app.config['TESTING'] = True

    def create_app(self):
        return app

    def setUp(self):
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()


class TestCreateLearningJourney(TestApp):
    def test_create_learning_Journey(self):
        lj1 = LearningJourney(Completion_Status="In Progress" ,Roles_id=2 ,Staff_ID=130001)
        db.session.add(lj1)
        db.session.commit()

        request_body = {
            'Completion_Status': lj1.Completion_Status,
            'Roles_id': lj1.Roles_id,
            'Staff_ID': lj1.Staff_ID
        }

        response = self.client.post("/createLJ",
                                    data=json.dumps(request_body),
                                    content_type='application/json')
        #print("LJ response.json")
        #print(response.json)
        self.assertEqual(response.json, {
            
            "data": {
                "Completion_Status": "In Progress",
                "Roles_id": 2,
                "Staff_ID": 130001,
                "id": 2
            },
            "message": "Learning Journey Created!"
            
        })

class TestGetRole(TestApp):
    def test_get_all_roles(self):
        role_1 = Role(name = 'Project Manager', description = 'A Project Manager manages a team of people.')
        role_2 = Role(name = 'Data Analyst', description = 'A Data Analyst reviews data to identify key insights.')
        role_3 = Role(name = 'Data Scientist', description = 'A Data Scientist analyze data for actionable insights.')
        db.session.add(role_1)
        db.session.add(role_2)
        db.session.add(role_3)
        db.session.commit()

        response = self.client.get("/roles",
                                    content_type='application/json')

        self.assertEqual(response.json, {
            "data": [
                        {
                            'description': 'A Project Manager manages a team of people.',
                            'id': 1,
                            'isDeleted' : 0,
                            'name': 'Project Manager'
                        },
                        {
                            'description': 'A Data Analyst reviews data to identify key insights.',
                            'id': 2,
                            'isDeleted' : 0,
                            'name': 'Data Analyst'
                        },
                        {
                            'description': 'A Data Scientist analyze data for actionable insights.',
                            'id': 3,
                            'isDeleted' : 0,
                            'name': 'Data Scientist'
                        }
                    ]
        })

    def test_get_role_by_id(self):
        role = Role(name = 'Project Manager', description = 'A Project Manager manages a team of people.')

        request_body = {
            'name': role.name,
            'description': role.description,
        }

        response = self.client.post("/roles_add",
                                    data=json.dumps(request_body),
                                    content_type='application/json')

        role_id = str(response.json['data']['id'])

        response_2 = self.client.get("/roles/" + role_id,
                                    content_type='application/json')
        
        self.assertEqual(response_2.json, {
            "data": {
                        'description': 'A Project Manager manages a team of people.',
                        'id': 1,
                        'isDeleted' : 0,
                        'name': 'Project Manager'
                    }         
        })

    def test_reject_invalid_get_role_by_id(self):
        role = Role(name = 'Project Manager', description = 'A Project Manager manages a team of people.')
        db.session.add(role)
        db.session.commit()

        role_id = "99"

        response = self.client.get("/roles/" + role_id,
                                    content_type='application/json')
        
        self.assertEqual(response.json, {
            "message": "Role not found."        
        })

class TestCreateRole(TestApp):
    def test_create_role(self):
        role1 = Role(name='Marketing Director' ,description='A Marketing Director is in charge of managing any given campaign.')

        request_body = {
            'name': role1.name,
            'description': role1.description,
        }
        #print('response body below')
        #print(request_body)

        response = self.client.post("/roles_add",
                                    data=json.dumps(request_body),
                                    content_type='application/json')
        #print('create role response.json below')
        #print(response.json)
        self.assertEqual(response.json, {
            
            "data": {
                'description': 'A Marketing Director is in charge of managing any given campaign.', 
                'id': 1, 
                'isDeleted': 0, 
                'name': 'Marketing Director'
            },
            "message": "Role Created!"
            
        })

    def test_reject_create_empty_role_name(self):

        request_body = {
            'name': '',
            'description': 'A Marketing Director is in charge of managing any given campaign.'
        }
        response = self.client.post("/roles_add",
                                    data= json.dumps(request_body),
                                    content_type='application/json')
        
        self.assertEqual(response.json, {
            "message": "Please fill in the Role name."
        })

    def test_reject_create_empty_role_desc(self):

        request_body = {
            'name': 'Marketing Director',
            'description': ''
        }
        response = self.client.post("/roles_add",
                                    data= json.dumps(request_body),
                                    content_type='application/json')
        
        self.assertEqual(response.json, {
            "message": "Please fill in the Role description."
        })

    def test_reject_create_duplicate_role(self):
        role_1 = Role(name = 'Marketing Director', description = 'A Marketing Director is in charge of managing any given campaign.')
        db.session.add(role_1)
        db.session.commit()

        request_body_1 = {
            'name': role_1.name,
            'description': role_1.description,
        }

        response1 = self.client.post("/roles_add",
                                    data= json.dumps(request_body_1),
                                    content_type='application/json')

        
        self.assertEqual(response1.json, {
            "message": "Role name already exists. Please enter unique role name."
        })

class TestUpdateRole(TestApp):
    def test_update_role(self):
        #print ("update role")
        existing_role = Role(name = 'Marketing Director', description = 'A Marketing Director is in charge of managing any given campaign.')
        updated_role = Role(name = 'Associate Marketing Director', description = 'An associate Marketing Director is in charge of assisting any given campaign.')

        request_body = {
            'name': existing_role.name,
            'description': existing_role.description
        }

        response = self.client.post("/roles_add",
                            data=json.dumps(request_body),
                            content_type='application/json')

        #print("RESPONSE ID: " + str(response.json['data']['id']))

        role_id = str(response.json['data']['id'])
        role_name = updated_role.name
        role_description = updated_role.description

        response_2 = self.client.put("/roles_update/" + role_id + "/" + role_name + "/" + role_description,
                                content_type='application/json')
        
        self.assertEqual(response_2.json, {
            "message": "Successfully updated!"          
        })

    def test_reject_update_duplicate_role(self):
            role = Role(name = 'Marketing Director', description = 'A Marketing Director is in charge of managing any given campaign.')

            request_body = {
                'name': role.name,
                'description': role.description
            }

            response = self.client.post("/roles_add",
                                data=json.dumps(request_body),
                                content_type='application/json')

            #print('responseid below:')
            #print("RESPONSE ID: " + str(response.json['data']['id']))

            role_id = str(response.json['data']['id'])
            role_name = role.name
            role_description = role.description

            response_2 = self.client.put("/roles_update/" + role_id + "/" + role_name + "/" + role_description,
                                    content_type='application/json')
            
            #print('response_2 below:')
            #print(response_2)
            self.assertEqual(response_2.json, {
                "message": "Role name already exists. Please enter unique role name."        
            })

class TestDeleteRole(TestApp):
    def test_delete_role(self):
        role = Role(name = 'Marketing Director', description = 'A Marketing Director is in charge of managing any given campaign.')

        request_body = {
            'name': role.name,
            'description': role.description
        }

        response = self.client.post("/roles_add",
                            data=json.dumps(request_body),
                            content_type='application/json')

        role_id = str(response.json['data']['id'])

        response_2 = self.client.delete("/role_delete/" + role_id, content_type='application/json') 

        self.assertEqual(response_2.json, {
                'data': {
                    'description': 'A Marketing Director is in charge of managing any given campaign.',
                    'id': 1,
                    'isDeleted': 1,
                    'name': 'Marketing Director'
            },
                'message': "Role successfully deleted."       
        }) 

class TestGetSkill(TestApp):
    def test_get_all_skills(self):
        skill_1 = Skill(name = 'Leadership', description = 'The key to successful leadership today is influence, not authority')
        skill_2 = Skill(name = 'Communication', description = 'Learn to communicate well in a team.')
        skill_3 = Skill(name = 'Project Management', description = 'Learn to manage projects well')
        db.session.add(skill_1)
        db.session.add(skill_2)
        db.session.add(skill_3)
        db.session.commit()

        response = self.client.get("/skills/",
                                    content_type='application/json')

        self.assertEqual(response.json, {
            "data": [
                        {
                            'description': 'The key to successful leadership today is influence, not authority',
                            'id': 1,
                            'isDeleted' : 0,
                            'name': 'Leadership'
                        },
                        {
                            'description': 'Learn to communicate well in a team.',
                            'id': 2,
                            'isDeleted' : 0,
                            'name': 'Communication'
                        },
                        {
                            'description': 'Learn to manage projects well',
                            'id': 3,
                            'isDeleted' : 0,
                            'name': 'Project Management'
                        }
                    ]
        })

    def test_get_skill_by_id(self):
        skill = Skill(name = 'Leadership', description = 'The key to successful leadership today is influence, not authority')

        request_body = {
            'name': skill.name,
            'description': skill.description,
        }

        response = self.client.post("/skills_add",
                                    data=json.dumps(request_body),
                                    content_type='application/json')

        skill_id = str(response.json['data']['id'])

        response_2 = self.client.get("/skills/" + skill_id,
                                    content_type='application/json')
        
        self.assertEqual(response_2.json, {
            "data": {
                        'description': 'The key to successful leadership today is influence, not authority',
                        'id': 1,
                        'isDeleted' : 0,
                        'name': 'Leadership'
                    }         
        })

    def test_reject_invalid_get_skill_by_id(self):
        skill = Skill(name = 'Leadership', description = 'The key to successful leadership today is influence, not authority')
        db.session.add(skill)
        db.session.commit()

        skill_id = "99"

        response = self.client.get("/skills/" + skill_id,
                                    content_type='application/json')
        
        self.assertEqual(response.json, {
            "message": "Skill not found."        
        })

class TestCreateSkill(TestApp):
    def test_create_skill(self):
        skill = Skill(name = 'Leadership', description = 'The key to successful leadership today is influence, not authority')

        request_body = {
            'name': skill.name,
            'description': skill.description,
        }

        response = self.client.post("/skills_add",
                                    data=json.dumps(request_body),
                                    content_type='application/json')

        self.assertEqual(response.json, {
            "data": {
                    'description': 'The key to successful leadership today is influence, not authority',
                    'id': 1,
                    'isDeleted' : 0,
                    'name': 'Leadership'
            },
            "message": "Skill Created!"
        })

    def test_reject_create_empty_skill_name(self):
        request_body = {
            'name': '',
            'description': 'Learn to communicate well in a team.'
        }
        response = self.client.post("/skills_add",
                                    data= json.dumps(request_body),
                                    content_type='application/json')
        
        self.assertEqual(response.json, {
            "message": "Please fill in the Skill name."
        })

    def test_reject_create_empty_skill_desc(self):
        request_body = {
            'name': 'Communication',
            'description': ''
        }
        response = self.client.post("/skills_add",
                                    data= json.dumps(request_body),
                                    content_type='application/json')
        
        self.assertEqual(response.json, {
            "message": "Please fill in the Skill description."
        })

    def test_reject_create_duplicate_skill(self):
        skill = Skill(name = 'Communication', description = 'Learn to communicate well in a team.')
        db.session.add(skill)
        db.session.commit()

        request_body = {
            'name': skill.name,
            'description': skill.description,
        }

        response = self.client.post("/skills_add",
                                    data= json.dumps(request_body),
                                    content_type='application/json')
        
        self.assertEqual(response.json, {
            "message": "Skill name already exists. Please enter unique skill name."
        })

class TestUpdateSkill(TestApp):
    def test_update_skill(self):
        #print ("update skill")
        existing_skill = Skill(name = 'Leadership', description = 'The key to successful leadership today is influence, not authority')
        updated_skill = Skill(name = 'Communication', description = 'Learn to communicate well in a team.')

        request_body = {
            'name': existing_skill.name,
            'description': existing_skill.description
        }

        response = self.client.post("/skills_add",
                            data=json.dumps(request_body),
                            content_type='application/json')

        #print("RESPONSE ID: " + str(response.json['data']['id']))

        skill_id = str(response.json['data']['id'])
        skill_name = updated_skill.name
        skill_description = updated_skill.description

        response_2 = self.client.put("/skills_update/" + skill_id + "/" + skill_name + "/" + skill_description,
                                content_type='application/json')
        
        self.assertEqual(response_2.json, {
            "message": "Successfully updated!"          
        })

    def test_reject_update_duplicate_skill(self):
        skill = Skill(name = 'Leadership', description = 'The key to successful leadership today is influence, not authority')

        request_body = {
            'name': skill.name,
            'description': skill.description
        }

        response = self.client.post("/skills_add",
                            data=json.dumps(request_body),
                            content_type='application/json')

        #print("RESPONSE ID: " + str(response.json['data']['id']))

        skill_id = str(response.json['data']['id'])
        skill_name = skill.name
        skill_description = skill.description

        response_2 = self.client.put("/skills_update/" + skill_id + "/" + skill_name + "/" + skill_description,
                                content_type='application/json')
        
        self.assertEqual(response_2.json, {
            "message": "Skill name already exists. Please enter unique skill name."        
        })
    

    #when valid_update is commented out
    #self.client.put just not routing to our app.py update function when skill name is empty

    #when valid_update is NOT commented out
    #self.client.put takes its input rather than the new input
    # def test_reject_update_empty_skill_name(self):
    #     print ("update skill")
    #     existing_skill = Skill(name = 'Leadership', description = 'The key to successful leadership today is influence, not authority')
    #     updated_skill = Skill(name = '', description = 'Test desc')

    #     request_body = {
    #         'name': existing_skill.name,
    #         'description': existing_skill.description
    #     }

    #     response = self.client.post("/skills_add",
    #                         data=json.dumps(request_body),
    #                         content_type='application/json')

    #     skill_id = str(response.json['data']['id'])
    #     skill_name = updated_skill.name
    #     skill_description = updated_skill.description

    #     print("Skill ID: " + skill_id)
    #     print("Skill Name: " + skill_name)
    #     print("Skill Desc: " + skill_description)

    #     response_2 = self.client.put("/skills_update/" + skill_id + "/" + skill_name + "/" + skill_description,
    #                         content_type='application/json')
        
    #     self.assertEqual(response_2.json, {
    #         "message": "There are empty fields, please enter the Skill Name."          
    #     })


    #when valid_update is commented out
    #self.client.put just not routing to our app.py update function when skill name is empty

    #when valid_update is NOT commented out
    #self.client.put takes its input rather than the new input
    # def test_reject_update_empty_skill_desc(self):
    #     print ("update skill")
    #     existing_skill = Skill(name = 'Leadership', description = 'The key to successful leadership today is influence, not authority')
    #     updated_skill = Skill(name = 'Test name', description = '')

    #     request_body = {
    #         'name': existing_skill.name,
    #         'description': existing_skill.description
    #     }

    #     response = self.client.post("/skills_add",
    #                         data=json.dumps(request_body),
    #                         content_type='application/json')

    #     skill_id = str(response.json['data']['id'])
    #     skill_name = updated_skill.name
    #     skill_description = updated_skill.description

    #     print("Skill ID: " + skill_id)
    #     print("Skill Name: " + skill_name)
    #     print("Skill Desc: " + skill_description)

    #     response_2 = self.client.put("/skills_update/" + skill_id + "/" + skill_name + "/" + skill_description,
    #                         content_type='application/json')
        
    #     self.assertEqual(response_2.json, {
    #         "message": "There are empty fields, please enter the Skill Description."          
    #     })

class TestDeleteSkill(TestApp):
    def test_delete_skill(self):
        skill = Skill(name = 'Communication', description = 'Learn to communicate well in a team.')

        request_body = {
            'name': skill.name,
            'description': skill.description
        }

        response = self.client.post("/skills_add",
                            data=json.dumps(request_body),
                            content_type='application/json')

        print ("Response: " + str(response.json))

        skill_id = str(response.json['data']['id'])
        print("Skill ID: " + skill_id)

        response_2 = self.client.delete("/skill_delete/" + skill_id, content_type='application/json') 

        self.assertEqual(response_2.json, {
                'data': {
                    'description': 'Learn to communicate well in a team.',
                    'id': 1,
                    'isDeleted': 1,
                    'name': 'Communication'
            },
                'message': "Skill successfully deleted."       
        })       



        # "data": {
        #             'description': 'Test Skill Description',
        #             'id': 1,
        #             'isDeleted' : 0,
        #             'name': 'Test Skill Name'
        #     },
        #     "message": "Skill Created!"


class TestAssignSkillToCourse(TestApp):
    def test_assign_skill_to_course(self):
        course_skill = Course_Skill(Course_id = 'MGT001', Skill_id = 1)
        db.session.add(course_skill)
        db.session.commit()

        request_body = {
            'Course_id': course_skill.Course_id,
            'Skill_id': course_skill.Skill_id,
        }
        # print('b4 assign skill to course')
        
        response = self.client.post("/assignskilltocourse/",
                                    data=json.dumps(request_body),
                                    content_type='application/json')

        # print ("Response: " + str(response.json))

        self.assertEqual(response.json, {
            
            "message": "added successfully"
        })

class TestAssignSkillToRole(TestApp):
    def test_assign_skill_to_role(self):
        role_skill = Role_Skill(roles_id = 3, skills_id = 2)
        db.session.add(role_skill)
        db.session.commit()

        request_body = {
            'roles_id': 3,
            'skills_id': 2,
        }
        # print('b4 assign skill to role')
        
        response = self.client.post("/assignskilltorole/",
                                    data=json.dumps(request_body),
                                    content_type='application/json')
        # print ("Response: " + str(response.json))

        self.assertEqual(response.json, {
            
            "message": "added successfully"
        })

class TestDeassignSkillToCourse(TestApp):
    def test_deassign_skill_to_course(self):
        course_skill = Course_Skill(Course_id = 'MGT001', Skill_id = 3)
        db.session.add(course_skill)
        db.session.commit()
        
        response = self.client.delete("/deassignskilltocourse/" + 'MGT001' + '/'  + '3' , content_type='application/json') 

        self.assertEqual(response.json, {
            
            "message": "deleted successfully"
        })      
class TestDeassignSkillToRole(TestApp):
    def test_deassign_skill_to_role(self):
        
        role_skill = Role_Skill(roles_id = 3, skills_id = 3)
        db.session.add(role_skill)
        db.session.commit()
        

        response = self.client.delete("/deassignskilltorole/" + '3' + '/'  + '3' , content_type='application/json') 

        self.assertEqual(response.json, {
            
            "message": "deleted successfully"
        })      





if __name__ == '__main__':
    unittest.main()
