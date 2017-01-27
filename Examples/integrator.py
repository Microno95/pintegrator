from __future__ import division
from __future__ import absolute_import
import desolver as odesolver
import sys
from io import open


def main():
    import os
    import math
    import sys

    if len(sys.argv) == 1:
        n = int(raw_input(u"Please enter the order of the system: N = "))
        if raw_input(u"Would you like to enter the system in vector form? ").replace(u" ", u"").lower() in [u"yes", u"1", u"y"]:
            vectorised = 1
        else:
            vectorised = 0
        eqn = []
        y_i = []
        stpsz = 1
        tlim = [0., 1.]
        if vectorised == 0:
            for i in xrange(n):
                eqn.append(raw_input(u"Please enter the ode using y_# and t as the variables: y_" + unicode(i) + u"' = "))
                eqn[i] = eqn[i].replace(u'^', u'**')
                print eqn
                y_i.append(float(raw_input(u"Please enter the initial value for this variable: y(" + unicode(i) + u") = ")))
                tlim = [float(raw_input(u"Please enter the initial time: t_initial = ")),
                        float(raw_input(u"Please enter the final time: t_final = "))]
                stpsz = float(raw_input(u"Please enter a step size for the integration: h = "))
        else:
            eqn = [equn.replace(u"^", u"**") for equn in raw_input(u"Please enter each ode separated by a comma using y_n as "
                                                             u"the variables for n between 0 and {}: "
                                                             u"\n".format(n - 1)).replace(u" ", u"").split(u",")]
            print eqn
            while len(eqn) != n:
                eqn = [equn.replace(u"^", u"**") for equn in raw_input(u"You have entered {} odes when {} odes were required. "
                                                                 u"\n".format(len(eqn), n)).replace(u" ", u"").split(u",")]
            y_i = [float(y_initial) for y_initial in raw_input(u"Please enter the initial values separated by a comma for "
                                                           u"each y_n for n between "
                                                           u"0 and {}: \n".format(n - 1)).replace(u" ", u"").split(u",")]
            while len(y_i) != n:
                y_i = [float(y_initial) for y_initial in raw_input(u"You have entered {} initial conditions "
                                                               u"when {} initial conditions were required. "
                                                               u"\n".format(len(y_i), n)).replace(u" ", u"").split(u",")]
            time_param = raw_input(u"Please enter the lower and upper time limits, and step size separated by commas: "
                               u"\n").replace(u" ", u"").split(u",")
            while len(time_param) != 3:
                time_param = raw_input(u"You have entered {} parameters when 3 were required. "
                                   u"\n".format(len(time_param))).replace(u" ", u"").split(u",")
            tlim = [float(time_param[0]), float(time_param[1])]
            stpsz = float(time_param[2])
    else:
        argu = sys.argv
        try:
            y_i = [float(i) for i in argu[argu.index(u'-y_i') + 1:argu.index(u'-tp')]]
            eqn = [i for i in argu[argu.index(u'-eqn') + 1:argu.index(u'-y_i')]]
            tlim = [float(i) for i in argu[argu.index(u'-tp') + 1:argu.index(u'-o')]]
            n = len(eqn)
            stpsz = tlim[-1]
            tlim = tlim[0:2]
        except ValueError:
            raise ValueError
    
    intobj = odesolver.OdeSystem(equ=eqn, y_i=y_i, t=tlim, savetraj=1, stpsz=stpsz, eta=1)
    if u'-m' not in sys.argv:
        if not raw_input(u"Would you like to explicitly choose the method of integration? ").replace(u' ', u'').lower() in \
                [u"no", u"0", u"do not do this to me", u""]:
            print u"Choose from one of the following methods: "
            shorthand = dict()
            c = 1
            for keys in sorted(odesolver.OdeSystem.available_methods()):
                print u"{}: {}".format(c, keys),; sys.stdout.write(u', ')
                shorthand.update({unicode(c): keys})
                c += 1
            print u"\n"
            intmethod = raw_input(u"Please enter the name of the method you would like to use, "
                              u"you may use numbers to refer to the methods available: ")
            if intmethod in shorthand:
                intmethod = shorthand[intmethod]
            while intmethod not in odesolver.OdeSystem.available_methods():
                intmethod = raw_input(u"That is not an available method, "
                                  u"please enter the name of the method you would like to use: ")
                if intmethod in shorthand:
                    intmethod = shorthand[intmethod]
        else:
            intmethod = u"Explicit Runge-Kutta 4"
    else:
        intmethod = sys.argv[sys.argv.index(u'-m') + 1]
    plotbool = raw_input(u"Would you like to make some basic plots? (Yes: 1, No: 0) : ")
    if len(sys.argv) > 1:
        savedir = sys.argv[sys.argv.index(u'-o') + 1]
    else:
        savedir = raw_input(u"Please enter the path to save data and plots to: ")

    reservedchars = [u'<', u'>', u'"', u'/', u'|', u'?', u'*']

    for i in reservedchars:
        while i in savedir:
            print u"Your save directory contains one of the following invalid characters{}".format(reservedchars)
            savedir = raw_input(u" please enter a new save directory: ")
    if savedir[-1] != u"\ ".strip():
        savedir += u"\ ".strip()

    if not os.path.isdir(savedir):
        os.makedirs(savedir)

    intobj.set_method(intmethod)
    intobj.integrate()

    res = intobj.final_conditions(p=0)
    vardicto = {}
    vardicto.update({u't': res[-1]})

    for i in xrange(n):
        vardicto.update({u'y_{}'.format(i): res[i]})

    for i in xrange(n):
        file = open(u"{}{}.txt".format(savedir, u"y_{}".format(i)), u'w')
        file.truncate()
        file.write((unicode(vardicto[u"y_{}".format(i)]).replace(u"[", u"")).replace(u"]", u""))
        file.close()

    file = open(u"{}time.txt".format(savedir), u'w')
    file.truncate()
    file.write(unicode(vardicto[u"t"]))
    file.close()

    initial_cond = u""

    for kp in xrange(n):
        initial_cond += u"y_{}({}) = {}\n".format(kp, tlim[0], y_i[kp])
    for kp in xrange(2):
        initial_cond += u"t_{} = {}\n".format(kp, tlim[kp])
    initial_cond += u"Step Size - h = {}\n".format(stpsz)

    file = open(u"{}initialcond.txt".format(savedir), u'w')
    file.truncate()
    file.write(initial_cond)
    file.close()

    if plotbool.strip() == u"1":
        import matplotlib.pyplot as plt
        import matplotlib as mplt

        font = {u'family': u'serif',
                u'weight': u'normal',
                u'size': 6}
        mplt.rc(u'font', **font)
        temp = raw_input(u"Please enter variables as pairs (x-axis first) separated by commas eq. y_0, y_1; t, y_0: ")
        temp = temp.replace(u" ", u"")
        titles = []
        plotvars = []
        pltcount = len(temp.split(u';'))
        scatter = []
        mu = []

        if temp != u"":
            for i in xrange(pltcount):
                print u"For plot {} please enter the following: ".format(i)
                titles.append([raw_input(u"Plot Title: "), raw_input(u"x-axis Title: "), raw_input(u"y-axis Title: ")])
                scatter.append(raw_input(u"Scatter(S) or Line(L) plot: "))
                p = float(raw_input(u"Please enter the period of sampling where the period is between {} and {}: P ="
                                u" ".format(math.copysign(stpsz, tlim[1] - tlim[0]), tlim[1] - tlim[0])))
                mu.append(int(abs(p / stpsz)))
                plotvars.append([vardicto[temp.split(u';')[i].split(u',')[0]],
                                 vardicto[temp.split(u';')[i].split(u',')[1]]])

            fig = []

            for i in xrange(pltcount):
                fig.append(plt.figure(i, figsize=(24, 24), dpi=600))
                ax = fig[i].add_subplot(111)
                if scatter[i].strip().lower() == u"s":
                    ax.scatter(plotvars[i][0][0:-1:mu[i]], plotvars[i][1][0:-1:mu[i]], s=0.25, marker=u'.')
                else:
                    ax.plot(plotvars[i][0][0:-1:mu[i]], plotvars[i][1][0:-1:mu[i]])
                ax.set_title(titles[i][0])
                ax.set_xlabel(titles[i][1])
                ax.set_ylabel(titles[i][2])
                ax.grid(True, which=u'both', linewidth=0.075)
                fig[i].savefig(u"{}{}.pdf".format(savedir, titles[i][0]), bbox_inches=u'tight')
                fig[i].savefig(u"{}{}.png".format(savedir, titles[i][0]), bbox_inches=u'tight')


if __name__ == u"__main__":
    main()
