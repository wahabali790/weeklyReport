import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
# Set the Matplotlib backend to 'Agg'
plt.switch_backend('Agg')
# Load the CSV files
data = pd.read_csv('./merged_BU_calendar_combined6.csv', low_memory=False)
data["Gender"] = data["Gender"].replace("Prefer not to say", "prefer not to say")
data["Brand_x"] = data["Brand_x"].replace("Outlet Adidas/Reebok", "Outlet AdidasReebok")
data["NPS"] = data["NPS"].replace("Detractor", "Detractors")
print(data["Brand_x"].value_counts())
survey_data = pd.read_csv('converted_surveystores1.csv', low_memory=False)
calender=pd.read_csv("Calendarx_2022_11.csv")

# Convert 'Submitted Date' to datetime format, coercing errors to NaT
data['Submitted Date'] = pd.to_datetime(data['Submitted Date'], format='%d/%m/%Y', errors='coerce')
print("n",data['Submitted Date'])
# Convert 'Date' to datetime format, coercing errors to NaT
survey_data['Date'] = pd.to_datetime(survey_data['Date'], format='%d/%m/%Y', errors='coerce')
#print()
# Convert 'Order Date' to datetime format, coercing errors to NaT
calender['Order Date'] = pd.to_datetime(calender['Order Date'], format='%d/%m/%Y', errors='coerce')

# Check the converted columns
print(survey_data['Date'])
print("o",calender['Order Date'])


# Function to get date range for continuous weeks from specified week and year
def get_date_range_for_continuous_week(week, year):
    # Filter data based 
    # on the given week and year
    week_data = calender[(calender['fiscal_week'] == week) & (calender['Year']==year)]
    
    if not week_data.empty:
        min_date = week_data['Order Date'].min()
        
        max_date = week_data['Order Date'].max()
        date_range_str = f"from {min_date.strftime('%d ')} to {max_date.strftime('%d %B %Y')}"
        return date_range_str
    
    return "Week or year not found"

# Define the function to create a blank pie chart
def create_blank_pie_chart(save_path):
    plt.figure(figsize=(3, 3))
    plt.pie([1], colors=['#CCCCCC'], startangle=90)
    plt.savefig(save_path)
    plt.close()

# Parameters
selected_week = 18
selected_year = "FY 24-25"


unique_bucodes = data[(data['fiscal_week'] == selected_week) & (data['Year'] == selected_year)&(data['Completion Status'] == "Completed")]['BUCode'].unique()

for bucode in unique_bucodes:
    filtered_data = data[(data['fiscal_week'] == selected_week) & (data['Year'] == selected_year) & (data['BUCode'] == bucode) & (data['Completion Status'] == "Completed")]
    #print(filtered_data)
    total_record = filtered_data["fiscal_week"].count()

    if not filtered_data.empty:
        experience_data = filtered_data["Please rate your experience today at STORE NAME"]
        happy_count = experience_data[experience_data == 'Happy'].count()
        sad_count = experience_data[experience_data == 'Sad'].count()
        normal_count = experience_data[experience_data == 'Normal'].count()
        total_responses = happy_count + sad_count + normal_count
        osat_percentage = int((happy_count / total_responses) * 100) if total_responses > 0 else 0

        bucode_data = data[data['BUCode'] == bucode]
        name = bucode_data['Brand_x'].iloc[0] if not bucode_data.empty else "N/A"
        country = bucode_data['Country'].iloc[0] if not bucode_data.empty else "N/A"
        store = bucode_data['Store'].iloc[0] if not bucode_data.empty else "N/A"
        date_range = get_date_range_for_continuous_week(selected_week, selected_year)

        nps_data = filtered_data['NPS']
        promoters = nps_data[nps_data == 'Promoter'].count()
        detractors = nps_data[nps_data == 'Detractors'].count()
        total_responses = len(nps_data)
        promoter_percentage = (promoters / total_responses) * 100 if total_responses > 0 else 0
        detractor_percentage = (detractors / total_responses) * 100 if total_responses > 0 else 0
        nps_score = round((promoter_percentage - detractor_percentage)) if total_responses > 0 else 0

        # Save gender pie chart
        gender_counts = filtered_data['Gender'].value_counts()
        color_order = {'Male': '#ff7e7e', 'Female': '#26d5fd', 'prefer not to say': '#5560ff'}
        colors = [color_order.get(gender, '#CCCCCC') for gender in gender_counts.index]
        if not gender_counts.empty:
            plt.figure(figsize=(3, 3))
            gender_counts.plot.pie(autopct='%1.1f%%',labels=None, startangle=90, colors=colors , wedgeprops=dict(width=0.3, edgecolor='w'))
            plt.title('')
            plt.ylabel('')  # Hide the y-label
            plt.savefig(f'./static/{bucode}_gender_pie_chart.png')
            plt.close()
        else:
            create_blank_pie_chart(f'./static/{bucode}_gender_pie_chart.png')

        # Filter survey data based on matching 'Submitted at' and 'Date'
        survey_week = calender[(calender['fiscal_week'] == selected_week) & (calender['Year']==selected_year)]
        print("h",filtered_data['Submitted Date'])
        matched_survey_data = survey_data[survey_data['Date'].isin(survey_week['Order Date'])&(survey_data["BUcode"]==bucode)]
        print("survey",matched_survey_data)

        # Count occurrences of each value in 'Device category'
        device_category_counts = matched_survey_data['Device category'].value_counts()
        total_device_counts = device_category_counts.sum()

        # Define color order for device categories
        device_color_order = {'mobile': '#ff7e7e', 'tablet': '#26d5fd', 'desktop': '#5560ff'}
        device_colors = [device_color_order.get(device, '#CCCCCC') for device in device_category_counts.index]

        # Plot pie chart for device category counts
        if not device_category_counts.empty:
            plt.figure(figsize=(3, 3))
            device_category_counts.plot.pie(autopct='%1.1f%%', startangle=90, colors=device_colors, wedgeprops=dict(width=0.3, edgecolor='w'))
            
            plt.ylabel('')  # Hide the y-label
            plt.savefig(f'./static/{bucode}_device_category_pie_chart.png')
            plt.close()
        else:
            create_blank_pie_chart(f'./static/{bucode}_device_category_pie_chart.png')


        # Save customer experience pie chart
        experience_counts = filtered_data['Please rate your experience today at STORE NAME'].value_counts()
        color_map = {'Happy': '#ff7e7e', 'Normal': '#26d5fd', 'Sad': '#5560ff'}

        colors_exp = [color_map.get(experience, '#CCCCCC') for experience in experience_counts.index]
        if not experience_counts.empty:
            plt.figure(figsize=(3, 3))
            experience_counts.plot.pie(autopct="%1.1f%%",labels=None, startangle=90, colors=colors_exp ,wedgeprops=dict(width=0.3, edgecolor='w'))
            plt.title('')
            plt.ylabel('')  # Hide the y-label
            plt.savefig(f'./static/{bucode}_customer_experience_pie_chart.png')
            plt.close()
        else:
            create_blank_pie_chart(f'./static/{bucode}_customer_experience_pie_chart.png')

        # Save visit frequency pie chart
        visit_frequency_counts = filtered_data['How frequently do you visit us?'].value_counts()
        visit_frequency_color_map = {'Occasionally': '#ff7e7e', 'Monthly': '#26d5fd', 'Weekly': '#5560ff'}

        visit_frequency_colors = [visit_frequency_color_map.get(frequency, '#CCCCCC') for frequency in visit_frequency_counts.index]
        if not visit_frequency_counts.empty:
            plt.figure(figsize=(3, 3))
            visit_frequency_counts.plot.pie(autopct="%1.1f%%",labels=None, startangle=90, colors=visit_frequency_colors ,wedgeprops=dict(width=0.3, edgecolor='w'))
            plt.title('')
            plt.ylabel('')  # Hide the y-label
            plt.savefig(f'./static/{bucode}_visit_frequency_pie_chart.png')
            plt.close()
        else:
            create_blank_pie_chart(f'./static/{bucode}_visit_frequency_pie_chart.png')

        # Save NPS pie chart
        nps_counts = filtered_data['NPS'].value_counts()
        nps_color_map = {'Detractors': '#ff7e7e', 'Passive': '#26d5fd', 'Promoter': '#5560ff'}

        nps_colors = [nps_color_map.get(nps, '#CCCCCC') for nps in nps_counts.index]
        if not nps_counts.empty:
            plt.figure(figsize=(3, 3))
            nps_counts.plot.pie(autopct="%1.1f%%", labels=None,startangle=90, colors=nps_colors ,wedgeprops=dict(width=0.3, edgecolor='w'))
            plt.title('')
            plt.ylabel('')  # Hide the y-label
            plt.savefig(f'./static/{bucode}_nps_pie_chart.png')
            plt.close()
        else:
            create_blank_pie_chart(f'./static/{bucode}_nps_pie_chart.png')

        # Save device category pie chart
    #         df_survay = pd.read_csv("surveystores1.csv")
    #         device_counts = df_survay['Device category'].value_counts()
    #         total_device_counts = device_category_counts.sum()
    #         device_color_map = {'mobile': '#ff7e7e', 'tablet': '#5560ff', 'desktop': '#26d5fd'}

    # # Generate the colors list based on the order of the device counts
    #         device_colors = [device_color_map.get(device, '#CCCCCC') for device in device_counts.index]
    #         if not device_counts.empty:
    #             plt.figure(figsize=(3, 3))
    #             device_counts.plot.pie(autopct="%1.1f%%",labels=None, startangle=90, colors=device_colors ,wedgeprops=dict(width=0.3, edgecolor='w'))
    #             plt.title('')
    #             plt.ylabel('')  # Hide the y-label
    #             plt.savefig(f'./static/{bucode}_device_pie_chart.png')
    #             plt.close()
    #         else:
    #             create_blank_pie_chart(f'./static/{bucode}_device_pie_chart.png')
        import arabic_reshaper
        from bidi.algorithm import get_display

        # Save the  row of feedback as an image
        def reshape_arabic_text(text):
            reshaped_text = arabic_reshaper.reshape(text)  # Reshape the text
            bidi_text = get_display(reshaped_text)  # Handle bidi text
            return bidi_text

        # Your existing code...
        filtered_data = filtered_data.dropna(subset=["Share your Feedback"])
        print("before", filtered_data)
        filtered_data['Share your Feedback'] = filtered_data['Share your Feedback'].str.slice(0, 115)
        filtered_data['Share your Feedback'] = filtered_data['Share your Feedback'].apply(reshape_arabic_text)

        filtered_data['Submitted Date'] = pd.to_datetime(filtered_data['Submitted Date']).dt.strftime('%d/%m/%Y')

        first_row = filtered_data[["Submitted Date", "Submitted Time", "Share your Feedback"]]
        print("f", first_row)

        fig = plt.figure(figsize=(10, 0.5))  # Increase the figure size to give more space
        gs = gridspec.GridSpec(1, 1)
        ax = fig.add_subplot(gs[0, 0])
        ax.axis('tight')
        ax.axis('off')

        # Check if first_row is empty
        if first_row.empty:
            # Create a blank image
            ax.text(0.5, 0.5, 'No data available', ha='center', va='center', fontsize=12)
        else:
            # Set column widths to ensure no overlap
            col_widths = [0.15, 0.15, 0.7]  # Adjust the widths as necessary

            tbl = ax.table(cellText=first_row.values, colLabels=first_row.columns, cellLoc='center', loc='center', colWidths=col_widths)
            tbl.auto_set_font_size(False)
            tbl.set_fontsize(8)  # Increase font size slightly
            tbl.scale(1.2, 1.2)  # Adjust scale as needed

            for key, cell in tbl.get_celld().items():
                if key[0] == 0:
                    cell.set_facecolor('skyblue')
                cell.set_edgecolor('white')

        image_path = f'./static/{bucode}_first_row.png'
        plt.savefig(image_path, bbox_inches='tight', dpi=300)
        plt.close()

        html_template = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ZARA Report</title>
</head>
<body style="font-family: Arial, sans-serif; margin: 0; padding: 0; background-color: #f7f7f7; width: 800px;">
    <div style="width: 100%;  max-width: 800px; margin: 20px auto; background-color: #f5f5fe; padding: 20px; box-shadow: 0 0 10px rgba(0,0,0,0.1);">
        <header style="display: table; width: 100%; border-spacing: 0; border-collapse: collapse;">
            <div style="display: table-cell; vertical-align: middle; text-align: left; width: 30%;">
                <img id="logo" src="./static/logoresized/{name}.png" alt="Logo Image" style="width: 130px; height: auto;">
            </div>
            <div style="display: table-cell; vertical-align: middle; text-align: center; width: 40%;">
                <div style="display: inline-block; text-align: center;">
                    
                    <div style="display: inline-block; vertical-align: middle; margin-left: 10px;">
                        <div style="font-size: 16px; font-weight: bold;"><img src="./static/countries/{country}.png" alt="Country Image" style="width: 30px; height: 20px; margin-right;">&nbsp;{country}</div>
                        <div style="font-size: 16px;">{store}</div>
                    </div>
                </div>
            </div>
            <div style="display: table-cell; vertical-align: middle; text-align: right; width: 100%;">
                <img id="week-image" src="./static/logoresized/Azadea.png" alt="Azadea Image" style="width: 100px; height: auto;">
                <div style="margin-top: 10px;">
                    <span style="font-size: 24px; font-weight: bold; margin-right: 20px;">Week {selected_week}</span>
                    <div style="font-size: 16px; margin-right: 20px;">{date_range}</div>
                </div>
            </div>
        </header>
        <main style="font-size:14px;font-weight: 550;">
            <div style="margin-top: 20px;">
    <div style="background-color: #ffffff; border: 1px solid #fff; border-radius: 8px; padding: 20px; box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);">
        <h2 style="margin-left: 20px; font-size: 18px;">Summary</h2>
        <p style="margin-left: 20px;">Weekly Summary</p>
        <div style="display: table; width: 100%; border-spacing: 20px;">
            <div style="width: 30%; background-color: #ffe0e0; padding: 10px; border-radius: 8px; text-align: center; height: 200px; display: table-cell; vertical-align: middle; box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);">
                <img src="./static/totalresponse.PNG" alt="Total Responses Image" style="width: 90px; height: 80px;">
                <div style="font-size: 16px; font-weight: bold;">Total Responses</div>
                <div style="font-size: 44px; font-weight: bold; margin: 20px 0; color: {'#fe7d7d' if total_record < 25 else '#000000'};">
                    {total_record}
                </div>
                <div style="font-size: 14px; color: #888;">Weekly Target: 25</div>
            </div>
            <div style="width: 30%; background-color: #ffe0f0; padding: 10px; border-radius: 8px; text-align: center; height: 200px; display: table-cell; vertical-align: middle; box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);">
                <img src="./static/nps.png" alt="NPS Image" style="width: 70px; height: 70px;">
                <div style="font-size: 16px; font-weight: bold;">NET Promoter Score</div>
                <div style="font-size: 44px; font-weight: bold; margin: 20px 0; color: {'#fe7d7d' if nps_score < 80 else '#000000'};">
                    {nps_score}
                </div>
                <div style="font-size: 14px; color: #888;">NPS Target: 80</div>
            </div>
            <div style="width: 30%; background-color: #e0ffe0; padding: 10px; border-radius: 8px; text-align: center; height: 200px; display: table-cell; vertical-align: middle; box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);">
                <img src="./static/osat.png" alt="OSAT Image" style="width: 100px; height: 80px;">
                <div style="font-size: 16px; font-weight: bold;">OSAT Score</div>
                <div style="font-size: 44px; font-weight: bold; margin: 20px 0; color: {'#fe7d7d' if osat_percentage < 85 else '#000000'};">
                    {osat_percentage}
                </div>
                <div style="font-size: 14px; color: #888;">OSAT Target: 85%</div>
            </div>
        </div>
    </div>
</div>
            <div style="display: table; width: 100%; border-spacing: 20px; margin-top: 20px;">
                <div style="width: 45%; background-color: #fff; padding: 20px; border-radius: 8px; box-shadow: 0 0 10px rgba(0,0,0,0.1); display: table-cell; vertical-align: middle; text-align: left;">
                    <h3 style="font-size: 18px; font-weight: bold; margin: 0 0 10px 0;">Customer Gender</h3>
                    <div style="margin-top: 20px; display: flex; justify-content: space-between;">
                        <div>
                                <div style="margin-bottom: 10px;">
                                    <span style="background-color: #ff7e7e; color: #fff; padding: 5px 10px; border-radius: 10px; font-weight: bold;">
                                        {gender_counts.get('Male', 0)}
                                    </span>   
                                      &nbsp;&nbsp;Male
                                </div>
                                <div style="margin-bottom: 10px;">
                                    <span style="background-color: #26d5fd; color: #fff; padding: 5px 10px; border-radius: 10px; font-weight: bold;">
                                        {gender_counts.get('Female', 0)}
                                    </span> 
                                    &nbsp;&nbsp;Female
                                </div>
                                <div style="margin-bottom: 10px;">
                                    <span style="background-color: #5560ff; color: #fff; padding: 5px 10px; border-radius: 10px; font-weight: bold;">
                                        {gender_counts.get('prefer not to say', 0)}
                                    </span> 
                                    &nbsp;&nbsp;Prefer not to say
                                </div>
                        </div>

                        <img src="./static/{bucode}_gender_pie_chart.png" alt="Gender Pie Chart" style="width: 250px; height: 250px;">
                    </div>
                    <p style="font-size: 14px; color: #888; text-align: center; margin-top: 20px;">Unveiling Gender Distribution</p>
                </div>
                <div style="width: 45%; background-color: #fff; padding: 20px; border-radius: 8px; box-shadow: 0 0 10px rgba(0,0,0,0.1); display: table-cell; vertical-align: middle; text-align: left;">
                    <h3 style="font-size: 18px; font-weight: bold; margin: 0 0 10px 0;">Customer Experience</h3>
                    <div style="margin-top: 20px; display: flex; justify-content: space-between;">
                        <div>
                            <div style="margin-bottom: 10px;">
                                <span style="background-color: #ff7e7e; color: #fff; padding: 5px 10px; border-radius: 10px; font-weight: bold;">
                                    {experience_counts.get('Happy', 0)}
                                </span> 
                                &nbsp;&nbsp;Happy
                            </div>
                            <div style="margin-bottom: 10px;">
                                <span style="background-color: #26d5fd; color: #fff; padding: 5px 10px; border-radius: 10px; font-weight: bold;">
                                    {experience_counts.get('Normal', 0)}
                                </span> 
                                &nbsp;&nbsp;Normal
                            </div>
                            <div style="margin-bottom: 10px;">
                                <span style="background-color: #5560ff; color: #fff; padding: 5px 10px; border-radius: 10px; font-weight: bold;">
                                    {experience_counts.get('Sad', 0)}
                                </span> 
                                &nbsp;&nbsp;Sad
                            </div>
                        </div>

                        <img src="./static/{bucode}_customer_experience_pie_chart.png" alt="Customer Experience Pie Chart" style="width: 250px; height: 250px;">
                    </div>
                    <p style="font-size: 14px; color: #888; text-align: center; margin-top: 20px;">Tracking Customer Satisfaction Levels</p>
                </div>
            </div>
            <div style="display: table; width: 100%; border-spacing: 20px; margin-top: 20px;">
                <div style="width: 45%; background-color: #fff; padding: 20px; border-radius: 8px; box-shadow: 0 0 10px rgba(0,0,0,0.1); display: table-cell; vertical-align: middle; text-align: left; margin-right: 500px;">
                    <h3 style="font-size: 18px; font-weight: bold; margin: 0 0 10px 0;">Customer Rating (NPS)</h3>
                    <div style="margin-top: 20px; display: flex; justify-content: space-between;">
                        <div>
                            <div style="margin-bottom: 10px;">
                                <span style="background-color: #ff7e7e; color: #fff; padding: 5px 10px; border-radius: 10px; font-weight: bold;">
                                    {nps_counts.get('Detractors', 0)}
                                </span> 
                                &nbsp;&nbsp;Detractors
                            </div>
                            <div style="margin-bottom: 10px;">
                                <span style="background-color: #26d5fd; color: #fff; padding: 5px 10px; border-radius: 10px; font-weight: bold;">
                                    {nps_counts.get('Passive', 0)}
                                </span> 
                                &nbsp;&nbsp;Passive
                            </div>
                            <div style="margin-bottom: 10px;">
                                <span style="background-color: #5560ff; color: #fff; padding: 5px 10px; border-radius: 10px; font-weight: bold;">
                                    {nps_counts.get('Promoter', 0)}
                                </span> 
                                &nbsp;&nbsp;Promoter
                            </div>
                        </div>

                        <img src="./static/{bucode}_nps_pie_chart.png" alt="NPS Pie Chart" style="width: 250px; height: 250px;">
                    </div>
                    <p style="font-size: 14px; color: #888; text-align: center; margin-top: 20px;">NPS Pie: Customer Sentiment in a Slice</p>
                </div>
                <div style="width: 45%; background-color: #fff; padding: 20px; border-radius: 8px; box-shadow: 0 0 10px rgba(0,0,0,0.1); display: table-cell; vertical-align: middle; text-align: left; position: relative; height: 300px;">
                    <h3 style="font-size: 18px; font-weight: bold; margin: 0 0 10px 0; position: absolute; top: 20px; left: 20px;"></h3>
                    <div style="margin-top: 20px;">
                        <img src="./static/icon.PNG" alt="NET Promoter Score Image" style="float: right; width: auto; height: auto;">
                    </div>
<p style="font-size: 14px; color: #888; text-align: center; margin: 0; position: relative; top: 1in;">NET Promoter Score=%Promoters - %Detractors</p>
                </div>




            </div>
            <div style="display: table; width: 100%; border-spacing: 20px; margin-top: 20px;">
                <div style="width: 45%; background-color: #fff; padding: 20px; border-radius: 8px; box-shadow: 0 0 10px rgba(0,0,0,0.1); display: table-cell; vertical-align: middle; text-align: left;">
                    <h3 style="font-size: 18px; font-weight: bold; margin: 0 0 10px 0;">Customer Visit Frequency</h3>
                    <div style="margin-top: 20px; display: flex; justify-content: space-between;">
                        <div>
                            <div style="margin-bottom: 10px;">
                                <span style="background-color: #ff7e7e; color: #fff; padding: 5px 10px; border-radius: 10px; font-weight: bold;">
                                    {visit_frequency_counts.get('Occasionally', 0)}
                                </span> 
                                &nbsp;&nbsp;Occasionally
                            </div>
                            <div style="margin-bottom: 10px;">
                                <span style="background-color: #26d5fd; color: #fff; padding: 5px 10px; border-radius: 10px; font-weight: bold;">
                                    {visit_frequency_counts.get('Monthly', 0)}
                                </span> 
                                &nbsp;&nbsp;Monthly
                            </div>
                            <div style="margin-bottom: 10px;">
                                <span style="background-color: #5560ff; color: #fff; padding: 5px 10px; border-radius: 10px; font-weight: bold;">
                                    {visit_frequency_counts.get('Weekly', 0)}
                                </span> 
                                &nbsp;&nbsp;Weekly
                            </div>
                        </div>

                        <img src="./static/{bucode}_visit_frequency_pie_chart.png" alt="Visit Frequency Pie Chart" style="width: 250px; height: 250px;">
                    </div>
                    <p style="font-size: 14px; color: #888; text-align: center; margin-top: 20px;">Exploring Customer Visits</p>
                </div>
                <div style="width: 45%; background-color: #fff; padding: 20px; border-radius: 8px; box-shadow: 0 0 10px rgba(0,0,0,0.1); display: table-cell; vertical-align: middle; text-align: left;">
                        <h3 style="font-size: 18px; font-weight: bold; margin: 0 0 10px 0;">Device Category</h3>
                        <div style="margin-top: 20px; display: flex; justify-content: space-between;">
                            <div>
                                <div style="margin-bottom: 10px;">
                                    <span style="background-color: #ff7e7e; color: #fff; padding: 5px 10px; border-radius: 10px; font-weight: bold;">
                                        {0 if total_device_counts == 0 else (device_category_counts.get('mobile', 0) / total_device_counts) * 100:.0f}%
                                    </span> 
                                    &nbsp;&nbsp;Mobile
                                </div>
                                <div style="margin-bottom: 10px;">
                                    <span style="background-color: #26d5fd; color: #fff; padding: 5px 10px; border-radius: 10px; font-weight: bold;">
                                        {0 if total_device_counts == 0 else (device_category_counts.get('tablet', 0) / total_device_counts) * 100:.0f}%
                                    </span> 
                                    &nbsp;&nbsp;Tablet
                                </div>
                                <div style="margin-bottom: 10px;">
                                    <span style="background-color: #5560ff; color: #fff; padding: 5px 10px; border-radius: 10px; font-weight: bold;">
                                        {0 if total_device_counts == 0 else (device_category_counts.get('desktop', 0) / total_device_counts) * 100:.0f}%
                                    </span> 
                                    &nbsp;&nbsp;Desktop
                                </div>
                            </div>
                            <img src="./static/{bucode}_device_category_pie_chart.png" alt="Device Pie Chart" style="width: 250px; height: 250px;">
                        </div>
                        <p style="font-size: 14px; color: #888; text-align: center; margin-top: 20px;">Device Usage Insights</p>
                    </div>
            </div>
            <div style="display: table; width: 100%; margin-top: 20px;">
                <div style="width: 100%; text-align: center;">
                    <img src="./static/{bucode}_first_row.png" alt="First Row of CSV" style="max-width: 100%; height: auto; border-radius: 4px; padding: 5px; margin-top: 10px;">
                </div>
            </div>
        </main>
    </div>
</body>
</html>

"""
    # Save the HTML to a file
    html_file_path = f'./templates/{bucode}_index1.html'
    with open(html_file_path, 'w') as file:
        file.write(html_template)

print("HTML reports generated successfully!")
from flask import Flask, render_template, request
import pdfkit
import os

app = Flask(__name__)

# Render the HTML template dynamically based on BUCode
@app.route('/<bucode>')
def index(bucode):
    return render_template(f'{bucode}_index1.html')

# Generate PDFs for all BUCodes
@app.route('/generate-pdf')
def generate_all_pdfs():
    options = {
        'margin-top': '0.75in',
        'margin-right': '0.75in',
        'margin-bottom': '0.75in',
        'margin-left': '0.75in',
        'encoding': 'UTF-8',
        'no-outline': None,
        'print-media-type': None
    }
    
    unique_bucodes = data[(data['fiscal_week'] == selected_week) & (data['Year'] == selected_year)&(data['Completion Status'] == "Completed")]['BUCode'].unique()
    for bucode in unique_bucodes:
        url = f'http://localhost:5000/{bucode}'
        pdf_filename = f'{bucode}.pdf'
        pdf_filepath = os.path.join('pdfs1', pdf_filename)
        
        pdf = pdfkit.from_url(url, False, options=options)
        with open(pdf_filepath, 'wb') as f:
            f.write(pdf)
        
    return f"PDFs generated for BUCodes: {', '.join(unique_bucodes)}"

if __name__ == '__main__':
    app.run()
