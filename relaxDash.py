import numpy as np
import pandas as pd
import plotly.express as px
import io


class Relax():
    def __init__(self,val,data):
        self.sTime = []
        self.sFr = []
        self.sFr_e = []
        self.sTitre = []
        self.myrs='toto'
        self.PlotReturns=None

        if data=='':
            self.PlotReturns=None
            return

        dfData=pd.read_csv(io.StringIO(data[1:]),sep=',',lineterminator='$')
        #dfData = pd.read_excel('buffRelax.xlsx')
        dfData = dfData.replace('?', 0)
        dfData.to_csv('df.txt')
        self.groupData(dfData)
        strsplit = val.split(' ', 10)
        index = np.asanyarray(strsplit, dtype='int')
        if len(index)>=2:
            self.plotPlus(index)
        myData = self.list2DF()
        self.myplotly(myData)
        self.dataReturn=myData.to_csv(sep=',',line_terminator='\r')


    def myplotly(self,df):
        fig=px.line(df, x='time',y='R',error_y='dR',color='longName',symbol='longName' )
        fig.update_traces(marker={'size': 14})
        fig.update_layout(
            xaxis_title_text="time",
            xaxis_title_font_size=18,
            xaxis_tickfont_size=16,
            yaxis_title_text="Release",
            yaxis_title_font_size=18,
            yaxis_tickfont_size=16,
            hoverlabel_font_size=12,
            #autosize=True,
            #height=800
            #width=1200
        )
        fig.update_xaxes(automargin=True)
        fig.update_yaxes(automargin=True)
        #myrs=fig.write_html('my_figure.html', auto_open=True)
        #print(myrs)
        self.PlotReturns = fig

    def groupData(self,data):
        try:
            ref = data['ref']
        except:
            ref = data['Alt_Ref']
        data['longname'] = data['_IDsample'] + '/' + data['sample.titre'] + '/' + data['Export_sample.plus'].astype(
            str) + '/R' + ref.astype(str)
        grouped = data.groupby(['Export_FlagBad', 'longname'])
        for [flag, ln], group in grouped:
            if flag == 0:
                t = np.array(group['time_m'].astype(float))
                try:
                    Na = np.array(group['N'].astype(float))
                    dNa = np.array(group['N_e'].astype(float))
                    Nt = np.array(group['Nt'].astype(float))
                    dNt = np.array(group['Nt_e'].astype(float))
                except:
                    Na = np.array(group['Alt_N'].astype(float))
                    dNa = np.array(group['Alt_N_e'].astype(float))
                    Nt = np.array(group['Alt_Nt'].astype(float))
                    dNt = np.array(group['Alt_Nt_e'].astype(float))
                # end try
                dose = np.array(group['sample.Fluence'].astype(float))
                cp = 0
                R = np.zeros_like(Na)
                dR = np.zeros_like(Na)
                T = np.zeros_like(t)
                LN=[]
                for j in range(0, len(t)):
                    if j > 0:
                        cp = cp + Na[j - 1]
                    else:
                        cp = 0
                    R[j] = Nt[j] + cp
                    R[j] = R[j] / dose[0] * 1e8
                    T[j] = t[j] - t[0]
                    if Nt[j] > 0:
                        dR[j] = dNt[j] / Nt[j] * R[j]  # A REPRENDRE
                    else:
                        dR[j] = 0
                    LN.append(ln)
                # end for j

                self.sTime.append(T)
                self.sFr.append(R)
                self.sFr_e.append(dR)
                self.sTitre.append(LN)
            else:   #flag
                pass
        # end for group

    def list2DF(self):
        df = pd.DataFrame()
        for ln,T,R,dR in zip(self.sTitre,self.sTime,self.sFr,self.sFr_e):
            f0 = pd.DataFrame(list(zip(ln, T, R, dR)), columns=['longName', 'time', 'R', 'dR'])
            df = pd.concat([df, f0])
        return df

    def plotPlus(self, index):
        nt = [0]
        nF = [0]
        nFe = [0]
        nName=[]
        titre = ''
        for i in index:
            time = self.sTime[i]
            Fr = self.sFr[i]
            Fre = self.sFr_e[i]
            lt = nt[-1]
            xt = time + lt
            nt.extend(xt[1:])
            lf = nF[-1]
            xf = Fr + lf
            nF.extend(xf[1:])
            nFe.extend(Fre[1:])
            x = self.sTitre[i][0].split('/', 10)
            titre = titre + x[0] + '_'

        for j in range(0, len(nt)):
            nName.append(titre)
        # end for

        self.sTime.append(np.array(nt))
        self.sFr.append(np.array(nF))
        self.sFr_e.append(np.array(nFe))
        self.sTitre.append(nName)
