import matplotlib.pyplot as plt
import seaborn as sns

sns.set(rc={"figure.dpi":300, 'savefig.dpi':300})
sns.set_style('white')

def show_boxplot(data, title, x_label = "", y_label = "", store=False):
    fig, ax = plt.subplots(figsize=(15, 10))
    PROPS = {
        'boxprops':{'facecolor':'none', 'edgecolor':'red'},
        'medianprops':{'color':'green'},
        'whiskerprops':{'color':'blue'},
        'capprops':{'color':'magenta'}
    }

    sns.boxplot(x='NCPUS',y='ConsumedEnergy',
                data=data,
                showfliers=False,
                linewidth=1.5,
                ax=ax,
                **PROPS)

    sns.swarmplot(x='NCPUS', y='ConsumedEnergy',
                  data=data,
                  color=".25",
                  ax=ax)

    # Customize the plot
    #ax.set_title(title)
    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)

    if store:
        plt.savefig(
            f'{title}.png', dpi=300, bbox_inches='tight'
        )

    # Display the plot
    plt.show()
