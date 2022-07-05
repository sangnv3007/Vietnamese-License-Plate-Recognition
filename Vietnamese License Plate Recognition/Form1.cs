using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows.Forms;
using Emgu.CV;
using Emgu.CV.Structure;
using Emgu.CV.UI;
using Emgu.CV.CvEnum;

namespace Vietnamese_License_Plate_Recognition
{
    public partial class Form1 : Form
    {
        List<Image<Bgr, Byte>> PlateImagesList = new List<Image<Bgr, byte>>();
        public Form1()
        {
            InitializeComponent();
        }

        private void button1_Click(object sender, EventArgs e)
        {
            // open file dialog   
            OpenFileDialog open = new OpenFileDialog();
            // image filters  
            open.Filter = "Image Files(*.jpg; *.jpeg; *.gif; *.bmp)|*.jpg; *.jpeg; *.gif; *.bmp";
            if (open.ShowDialog() == DialogResult.OK)
            {
                // display image in picture box  
                string startupPath = open.FileName;
                Image<Rgb, Byte> img = new Image<Rgb, Byte>(startupPath);
                imageBox1.Image = img;
                Image<Gray, Byte> imgGray = new Image<Gray, Byte>(startupPath);
                pictureBox1.Image = imgGray.ToBitmap();
                ProcessImage(startupPath);
            }
        }

        public void ProcessImage(string startupPath)
        {
            Bitmap image = new Bitmap(startupPath);
            FindLicensePlate(image, pictureBox1, imageBox1, PlateImagesList, panel1);
        }

        private void FindLicensePlate(Bitmap image, PictureBox pictureBox1, ImageBox imageBox1, List<Image<Bgr, byte>> plateImagesList, Panel panel1)
        {
            try
            {
                Image<Bgr, byte> image2 = new Image<Bgr, byte>(image);
                CascadeClassifier classifier = new CascadeClassifier(Application.StartupPath + "\\output-hv-33-x25.xml");
                var imgGray = image2.Convert<Gray, byte>().Clone();
                Rectangle[] plates = classifier.DetectMultiScale(imgGray, 1.1, 4);
                //richTextBox1.Text = plates[0].ToString();
                if (plates.Length == 0)
                {
                    MessageBox.Show("Không thể nhận dạng được biển số xe này !", "TD SJC");
                    return;
                }

                foreach (Rectangle plate in plates)
                {
                    image2.Draw(plate, new Bgr(0, 255, 0), 2);
                }
                imageBox1.Image = image2;
                int x = plates[0].X;
                int y = plates[0].Y;
                int w = plates[0].Width;
                int h = plates[0].Height;
                Image<Bgr, byte> image3 = new Image<Bgr, byte>(image);
                image3.ROI = new Rectangle(x, y, w, h);
                pictureBox1.Image = image3.Bitmap;
            }
            catch (Exception ex)
            {
                MessageBox.Show(ex.Message);
            }
        }
    }
}
