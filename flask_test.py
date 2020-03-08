from flask import Flask, render_template, request, redirect
app = Flask(__name__)

global preferences
global preferences_with_weight
global final_rating

@app.route('/')
def hello_world():
   author = "ME 310 Team AREC"
   name = "ME 310 Team AREC"
   return render_template('index.html', author=author, name=name)

@app.route('/weight_input', methods = ['POST'])
def user_input():
   global preferences
   preferences_string = request.form['preferences_string']
   preferences = [x.strip() for x in preferences_string.split(',')]

   return render_template('weight_input.html', preferences=preferences)

@app.route('/score_input', methods = ['GET', 'POST'])
def weight_input():
   global preferences
   global preferences_with_weight
   preferences_with_weight = {}
   weights_list = request.form.getlist('feature_weight')
   for i in range(len(preferences)):
      print("i", i)
      preferences_with_weight[preferences[i]] = weights_list[i]

   return render_template('score_input.html', preferences=preferences, weights_list=weights_list)


@app.route('/display_rating', methods = ['GET', 'POST'])
def display_rating():
   global preferences
   global preferences_with_weight
   global final_rating

   final_rating = {}
   scores_list = request.form.getlist('score')
   for i in range(len(preferences)):
      final_rating[preferences[i]] = int(preferences_with_weight[preferences[i]]) * int(scores_list[i]) / 100
      final_rating_number = sum(final_rating.values())

   return render_template('display_rating.html', final_rating=final_rating, final_rating_number=final_rating_number)

if __name__ == "__main__":
    app.run()