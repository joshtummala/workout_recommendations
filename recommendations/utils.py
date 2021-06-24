from django.conf import settings
from django.utils.timezone import now

from neo4j import GraphDatabase
import urllib.request
from bs4 import BeautifulSoup
import csv 

class Neo4jUtils:
    """ Utils class to interact with neo4j """

    def __init__(
        self, 
        uri=settings.NEO4J_URI,
        username=settings.NEO4J_USERNAME,
        password=settings.NEO4J_PASSWORD
    ):
        self._driver = GraphDatabase.driver(uri, auth=(username, password), encrypted=False)
    
    @property
    def connection(self):
        return self._driver
    
    def close(self):
        self.connection.close()
    
    def session(self):
        return self.connection.session()
    
    def run(self, query):
        with self.session() as session:
            return session.run(query)


def date_now():
    """ Return the Date object of now """
    return now().date()

# read all exercises from the given webpage content
class WorkoutPlan:
	#default constructor
	def __init__(self):
		self.name = ""
		self.headers = []
		self.exercises = []

	# reads the workout plan
	def read_workout_plan(self, html):
		#read workout plan name
		key = "<h4>"
		start_index = html.find(key)
		if start_index == -1:
			return None

		#read workout plan name
		end_index = html.find("</h4>", start_index)
		self.name = html[start_index+len(key):end_index]
		self.name = self.name.strip(" ,\n\r")

		# read exercises table data now
		soup = BeautifulSoup(html[end_index+len(key)+1:], 'lxml')
		table_data = soup.find("table")

		# headers - "Exercise","Sets","Reps","Name"
		for i in table_data.find_all('th'):
			title = i.text.strip()
			self.headers.append(title)
			self.headers.append("Name")

		# exercises -
		for j in table_data.find_all('tr'):
			row_data = j.find_all('td')
			row = [tr.text.strip() for tr in row_data]
			row.append(self.name)
			if len(row) == 0 or len(row) == 1:
				continue
			else:
				self.exercises.append(row)

		return self


# read all workout plans from the given webpage url
class WorkoutPlanBook:
	#default constructor
	def __init__(self):
		self.plans = []

	def read_all_workout_plans(self, url):
		print("Scraping website: " + url)
		request = urllib.request.Request(url)
		request.add_header("User-Agent", "Mozilla/5.0 (X11; U; Linux i686) Gecko/20071127 Firefox/2.0.0.11")

		#read the data from the URL and print it
		page = urllib.request.urlopen(request)
		html = page.read().decode("utf-8")

		#read all workout plans
		while True:
			#All exercises content start at HTML tag <h4>, <h4 Day>, or <h4 Monday> and
			#end until the last table HTML tag </table> 
			start_index = html.find("<h4>")
			if start_index == -1:
				break

			end_index = html.find("</table>", start_index)
			if end_index == -1:
				break
			end_index += len("</table>")
			#get the exercises content - END

			#create a new workout plan with all exercises
			workout_plan = WorkoutPlan()
			exercises_section = html[start_index:end_index]
			workout_plan.read_workout_plan(exercises_section)
			self.plans.append(workout_plan)
			#print(workout_plan.headers)
			print(workout_plan.exercises)

			# reset the html page content for the next iteration 
			html = html[end_index:]

		return self


# main program
def scrape_workout_plans():
	# list of workout URLs to scrape
	urls = [ "https://www.muscleandstrength.com/workouts/limited-equipment-home-workout",
		"https://www.muscleandstrength.com/workouts/phul-workout",
		"https://www.muscleandstrength.com/workouts/6-day-dumbbell-only-workout",
		"https://www.muscleandstrength.com/workouts/dumbbell-only-upper-lower-workout-routine",
		"https://www.muscleandstrength.com/workouts/upper-lower-4-day-gym-bodybuilding-workout",
		"https://www.muscleandstrength.com/workouts/m-f-workout-routine",
		"https://www.muscleandstrength.com/workouts/4-day-maximum-mass-workout",
		"https://www.muscleandstrength.com/workouts/4-day-power-muscle-burn-workout-split.html",
		"https://www.muscleandstrength.com/workouts/6-week-workout-program-to-build-lean-muscle",
		"https://www.muscleandstrength.com/workouts/muscle-mania-10-week-muscle-growth-workout",
		"https://www.muscleandstrength.com/workouts/5-day-muscle-and-strength-building-workout-split",
		"https://www.muscleandstrength.com/workouts/dumbbell-only-home-or-gym-fullbody-workout.html",
		"https://www.muscleandstrength.com/workouts/michael-b-jordan-workout-program",
		"https://www.muscleandstrength.com/workouts/thor-ragnarok-chris-hemsworth-inspired-workout",
		"https://www.muscleandstrength.com/workouts/power-muscle-burn-5-day-powerbuilding-split.html",
		"https://www.muscleandstrength.com/workouts/10-week-mass-building-program.html",
		"https://www.muscleandstrength.com/workouts/muscle-and-strength-womens-workout",
		"https://www.muscleandstrength.com/workouts/muscle-and-strength-womens-fat-loss-workout",
		"https://www.muscleandstrength.com/workouts/best-full-body-workout-routine-for-women",
		"https://www.muscleandstrength.com/workouts/12-week-push-pull-legs-for-women",
		"https://www.muscleandstrength.com/workouts/10-week-upper-lower-workout-for-women",
		"https://www.muscleandstrength.com/workouts/8-week-full-body-womens-workout-routine",
		"https://www.muscleandstrength.com/workouts/12-week-womens-bikini-prep-workout",
		"https://www.muscleandstrength.com/workouts/abs-workout-women-8-weeks-flatter-stomach",
		"https://www.muscleandstrength.com/workouts/the-super-toning-training-routine.html",
		"https://www.muscleandstrength.com/workouts/8-week-beginner-workout-for-women",
		"https://www.muscleandstrength.com/workouts/the-butt-builder.html",
		"https://www.muscleandstrength.com/workouts/5-day-workout-routine-for-women" ]

	# create a workout_plans.csv file with the header "Exercise","Sets","Reps","Name"
	csvfile = open("workout_plans.csv", "w")
	csvwriter = csv.writer(csvfile)
	csvwriter.writerow(["Exercise","Sets","Reps", "Name"])

	index = 0
	while index < len(urls):
		planBook = WorkoutPlanBook()
		planBook.read_all_workout_plans(urls[index])
		index += 1

		# write scraped workout plans to the csv file
		for plan in planBook.plans:
			csvwriter.writerows(plan.exercises)
            
	print("---END---")