import matplotlib.pyplot as plt
import seaborn as sns

sns.set(rc={"figure.dpi":300, 'savefig.dpi':300})
sns.set_style('white')

def show_boxplot(data, title, metric, x_label = "", y_label = "", store=False):
    fig, ax = plt.subplots(figsize=(10, 8))
#    PROPS = {
#        'boxprops':{'facecolor':'none', 'edgecolor':'red'},
#        'medianprops':{'color':'green'},
#        'whiskerprops':{'color':'blue'},
#        'capprops':{'color':'magenta'}
#    }
    #PROPS = {
    #    'boxprops':{'facecolor': 'none', 'edgecolor':'gray'},
    #    'medianprops':{'color':'gray'},
    #    'whiskerprops':{'color':'gray'},
    #    'capprops':{'color':'gray'}
    #}

    PROPS = {
        'boxprops': {'facecolor': 'none', 'edgecolor': (0.1, 0.1, 0.1, 0.3)},
        'medianprops': {'color': (0.1, 0.1, 0.1, 0.3)},
        'whiskerprops': {'color': (0.1, 0.1, 0.1, 0.3)},
        'capprops': {'color': (0.1, 0.1, 0.1, 0.3)}
    }
    
    #sns.boxplot(x='NCPUS',y=metric,
    #            data=data,
    #            showfliers=False,
    #            linewidth=1.5,
    #            ax=ax,
    #            **PROPS)

    sns.violinplot(x='NCPUS',y=metric,
                data=data,
                ax=ax,
                fill=False,
                inner="quart",
                linewidth=2,
                width=1.1,
                density_norm='count'
    )
    
    sns.boxplot(x='NCPUS', y=metric,
                data=data,
                showfliers=False,
                linewidth=1.5,
                ax=ax,
                **PROPS)
 
    sns.swarmplot(x='NCPUS', y=metric,
                  data=data,
                  #color=".25",
                  color="red",
                  ax=ax)


    medians = data.groupby('NCPUS')[metric].median()
    ax.plot(range(len(medians)), medians.values, color='orange', linestyle='-', linewidth=3, marker='o', zorder=10)

    # Customize the plot
    #ax.set_title(title)
    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)

    if store:
        plt.savefig(
            f'{title}.pdf', dpi=300, bbox_inches='tight'
        )

    # Display the plot
    plt.show()
